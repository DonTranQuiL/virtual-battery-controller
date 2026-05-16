import logging
import statistics
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from .const import (
    DOMAIN, CONF_PRICE_SENSOR, CONF_CLIMATE_ENTITY, CONF_SWITCH_ENTITIES,
    CONF_MIN_TEMP, CONF_MAX_TEMP, CONF_SOLAR_EXPORT_SENSOR, CONF_AIRCO_WATTAGE,
    CONF_HVAC_MODE
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([VirtualBatteryCharging(hass, entry)])

class VirtualBatteryCharging(BinarySensorEntity):
    def __init__(self, hass, entry):
        self.hass = hass
        self._entry = entry
        self._attr_name = "Virtual Battery Arbitrage Charging"
        self._attr_unique_id = f"{entry.entry_id}_charging"
        self._attr_device_class = BinarySensorDeviceClass.POWER
        self._last_state = False

    @property
    def config_data(self):
        """Helper to merge options and initial data. Options take priority."""
        return {**self._entry.data, **self._entry.options}

    @property
    def device_info(self):
        """Link entity to parent device."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Virtual Battery",
            "manufacturer": "Custom Virtual Battery",
            "model": "VBC v1.0"
        }

    @property
    def extra_state_attributes(self):
        """Show the connected devices in the Home Assistant UI."""
        attributes = {
            "target_climate_device": self.config_data.get(CONF_CLIMATE_ENTITY),
            "hvac_mode": self.config_data.get(CONF_HVAC_MODE),
            "device_wattage": f"{self.config_data.get(CONF_AIRCO_WATTAGE)} W",
        }
        
        # Add the solar sensor if the user selected one
        solar_sensor = self.config_data.get(CONF_SOLAR_EXPORT_SENSOR)
        if solar_sensor:
            attributes["target_solar_sensor"] = solar_sensor
            
        # Add the list of smart plugs/relays if the user selected any
        switch_entities = self.config_data.get(CONF_SWITCH_ENTITIES, [])
        if switch_entities:
            # Join the list into a clean comma-separated string for the UI
            attributes["connected_switches"] = ", ".join(switch_entities)
            
        return attributes

    @property
    def is_on(self):
        airco_wattage = self.config_data.get(CONF_AIRCO_WATTAGE, 1000)

        # 2. Check Solar Export Override
        solar_sensor_id = self.config_data.get(CONF_SOLAR_EXPORT_SENSOR)
        if solar_sensor_id:
            solar_state = self.hass.states.get(solar_sensor_id)
            try:
                if solar_state and float(solar_state.state) >= airco_wattage:
                    _LOGGER.debug("Solar export covers wattage. Forcing charge.")
                    self._execute_charging(True)
                    return True
            except (ValueError, TypeError):
                pass

        # 3. Universal Price Arbitrage Logic
        price_sensor_id = self.config_data[CONF_PRICE_SENSOR]
        price_state = self.hass.states.get(price_sensor_id)
        
        if not price_state: 
            return False

        current_price = float(price_state.state)
        attrs = price_state.attributes

        # Auto-detect Enever/ENTSO-E/Nord Pool
        prices_list = None
        price_key = None
        if "all_prices" in attrs:       
            prices_list = attrs["all_prices"]
            if len(prices_list) > 0:
                if 'price_kwh' in prices_list[0]: 
                    price_key = 'price_kwh' # ENTSO-E
                elif 'prijs' in prices_list[0]: 
                    price_key = 'prijs'     # Enever

        try:
            # SCENARIO A: Found a forecast! Calculate dynamic threshold.
            if prices_list and price_key:
                all_values = [p[price_key] for p in prices_list]
                threshold = statistics.quantiles(all_values, n=4)[0] # Cheapest 25%
                avg_price = statistics.mean(all_values)
                is_cheap = current_price <= threshold
                
                # Track savings
                if is_cheap and not self._last_state:
                    self._log_savings(current_price, avg_price)

            # SCENARIO B: No forecast. Use static fallback threshold (10 cents).
            else:
                fallback_threshold = 0.10 
                is_cheap = current_price <= fallback_threshold
                if is_cheap and not self._last_state:
                    _LOGGER.info("Charging based on static fallback threshold.")

            # 4. Push commands to devices
            self._execute_charging(is_cheap)
            self._last_state = is_cheap
            return is_cheap

        except Exception as e:
            _LOGGER.error("Error in Virtual Battery Arbitrage: %s", e)
            return False

    def _execute_charging(self, charging):
        """Helper to fire off both climate and switch updates."""
        self._update_climate(charging)
        self._update_switches(charging)

    def _update_climate(self, charging):
        """Update the Airco setpoint based on Heating/Cooling and Charging state."""
        climate_id = self.config_data.get(CONF_CLIMATE_ENTITY)
        if not climate_id: 
            return

        hvac_mode = self.config_data.get(CONF_HVAC_MODE, "Heating")
        min_temp = self.config_data[CONF_MIN_TEMP]
        max_temp = self.config_data[CONF_MAX_TEMP]

        # INVERSION LOGIC for Heating/Cooling
        if hvac_mode == "Heating":
            # Heating: Charge by making it WARM (max_temp)
            target_temp = max_temp if charging else min_temp
        else:
            # Cooling: Charge by making it COLD (min_temp)
            target_temp = min_temp if charging else max_temp

        climate_state = self.hass.states.get(climate_id)
        if climate_state and climate_state.attributes.get("temperature") != target_temp:
            self.hass.async_create_task(
                self.hass.services.async_call("climate", "set_temperature", {"entity_id": climate_id, "temperature": target_temp})
            )

    def _update_switches(self, charging):
        """Update all smart plugs."""
        switch_ids = self.config_data.get(CONF_SWITCH_ENTITIES, [])
        if not switch_ids: return

        action = "turn_on" if charging else "turn_off"

        for entity_id in switch_ids:
            current_state = self.hass.states.get(entity_id)
            if current_state and current_state.state != ("on" if charging else "off"):
                domain = entity_id.split('.')[0] 
                self.hass.async_create_task(self.hass.services.async_call(domain, action, {"entity_id": entity_id}))

    def _log_savings(self, current_price, avg_price):
        """Estimate financial benefit."""
        wattage = self.config_data.get(CONF_AIRCO_WATTAGE, 0)
        saved = (avg_price - current_price) * (wattage / 1000)
        _LOGGER.info("Virtual Battery charging. Est. savings: %s EUR/hr", round(saved, 4))

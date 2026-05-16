from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from .const import DOMAIN, CONF_CLIMATE_ENTITY, CONF_MIN_TEMP, CONF_MAX_TEMP, CONF_HVAC_MODE

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([VirtualBatterySoC(hass, entry)])

class VirtualBatterySoC(SensorEntity):
    def __init__(self, hass, entry):
        self.hass = hass
        self._entry = entry
        self._attr_name = "Virtual Battery State of Charge"
        self._attr_unique_id = f"{entry.entry_id}_soc"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:battery-high"

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
    def native_value(self):
        """Calculate the percentage charge based on Heating or Cooling logic."""
        climate_id = self.config_data.get(CONF_CLIMATE_ENTITY)
        if not climate_id: 
            return None

        min_temp = self.config_data[CONF_MIN_TEMP]
        max_temp = self.config_data[CONF_MAX_TEMP]
        hvac_mode = self.config_data.get(CONF_HVAC_MODE, "Heating")
        
        state = self.hass.states.get(climate_id)
        if not state or "current_temperature" not in state.attributes:
            return None
        
        try:
            current_temp = float(state.attributes["current_temperature"])
        except (ValueError, TypeError):
            return None
        
        # INVERSION LOGIC for SoC %
        if hvac_mode == "Heating":
            # Heating: 100% full when room is WARM (max_temp)
            if current_temp >= max_temp: 
                return 100.0
            if current_temp <= min_temp: 
                return 0.0
            soc = ((current_temp - min_temp) / (max_temp - min_temp)) * 100
        else:
            # Cooling: 100% full when room is COLD (min_temp)
            if current_temp <= min_temp: 
                return 100.0
            if current_temp >= max_temp: 
                return 0.0
            soc = ((max_temp - current_temp) / (max_temp - min_temp)) * 100
            
        return round(float(soc), 1)

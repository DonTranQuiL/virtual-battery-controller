import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaOptionsFlowHandler,
    SchemaFlowFormStep,
)
from .const import (
    DOMAIN, CONF_PRICE_SENSOR, CONF_CLIMATE_ENTITY, CONF_SWITCH_ENTITIES,
    CONF_SOLAR_EXPORT_SENSOR, CONF_AIRCO_WATTAGE, CONF_MIN_TEMP, CONF_MAX_TEMP,
    CONF_HVAC_MODE, MODE_HEATING, MODE_COOLING
)

async def get_options_schema(handler):
    """Generate the options schema. handler is a SchemaCommonFlowHandler."""
    # FIXED: Access the config_entry through the parent_handler
    entry = handler.parent_handler.config_entry
    
    # Merge data and options
    data = {**entry.data, **entry.options}
    
    return vol.Schema({
        vol.Required(CONF_PRICE_SENSOR, default=data.get(CONF_PRICE_SENSOR) or ""): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Required(CONF_CLIMATE_ENTITY, default=data.get(CONF_CLIMATE_ENTITY) or ""): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="climate")
        ),
        vol.Optional(CONF_SWITCH_ENTITIES, default=data.get(CONF_SWITCH_ENTITIES) or []): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["switch", "input_boolean"], multiple=True)
        ),
        vol.Optional(CONF_SOLAR_EXPORT_SENSOR, default=data.get(CONF_SOLAR_EXPORT_SENSOR) or ""): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Required(CONF_HVAC_MODE, default=data.get(CONF_HVAC_MODE) or MODE_HEATING): vol.In([MODE_HEATING, MODE_COOLING]),
        vol.Required(CONF_AIRCO_WATTAGE, default=data.get(CONF_AIRCO_WATTAGE) or 1000): int,
        vol.Required(CONF_MIN_TEMP, default=data.get(CONF_MIN_TEMP) or 19): int,
        vol.Required(CONF_MAX_TEMP, default=data.get(CONF_MAX_TEMP) or 24): int,
    })

OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(get_options_schema)
}

class VirtualBatteryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Virtual Battery."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Virtual Battery", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_PRICE_SENSOR): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
                vol.Required(CONF_CLIMATE_ENTITY): selector.EntitySelector(selector.EntitySelectorConfig(domain="climate")),
                vol.Optional(CONF_SWITCH_ENTITIES): selector.EntitySelector(selector.EntitySelectorConfig(domain=["switch", "input_boolean"], multiple=True)),
                vol.Optional(CONF_SOLAR_EXPORT_SENSOR): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
                vol.Required(CONF_HVAC_MODE, default=MODE_HEATING): vol.In([MODE_HEATING, MODE_COOLING]),
                vol.Required(CONF_AIRCO_WATTAGE, default=1000): int,
                vol.Required(CONF_MIN_TEMP, default=19): int,
                vol.Required(CONF_MAX_TEMP, default=24): int,
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SchemaOptionsFlowHandler(config_entry, OPTIONS_FLOW)
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_NAME, CONF_DEVICE_TYPE, DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE

class HouseholdChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input, options={})

        schema = vol.Schema({
            vol.Required(CONF_NAME): str,
            vol.Required(CONF_DEVICE_TYPE, default=DEVICE_TYPE_CHORE): vol.In([DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE]),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_get_options_flow(self, entry):
        from .options_flow import HouseholdChoresOptionsFlow
        return HouseholdChoresOptionsFlow(entry)

import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_TITLE, CONF_TYPE, DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE


class ChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chores."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_TITLE], data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_TITLE): str,
            vol.Required(CONF_TYPE, default=DEVICE_TYPE_CHORE): vol.In([DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE]),
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

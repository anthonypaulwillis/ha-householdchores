import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_TITLE

class ChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chores."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Step when user adds the integration via UI."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_TITLE],
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required(CONF_TITLE): str
        })
        return self.async_show_form(step_id="user", data_schema=data_schema)

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class ChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Chores integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Step when user adds the integration via UI."""

        if user_input is not None:
            # The 'title' becomes the device name
            return self.async_create_entry(title=user_input["title"], data=user_input)

        # Show a form with a single field: title
        data_schema = vol.Schema({
            vol.Required("title"): str
        })

        return self.async_show_form(step_id="user", data_schema=data_schema)

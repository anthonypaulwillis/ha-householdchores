from homeassistant import config_entries
from .const import DOMAIN

class ChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chores."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Step when the user adds the integration via UI."""
        if user_input is not None:
            return self.async_create_entry(title="Chores", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema={},  # you can add fields here later
        )

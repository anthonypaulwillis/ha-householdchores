import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE


DEVICE_SCHEMA = vol.Schema({
    vol.Required("name"): str,
    vol.Required("device_type", default=DEVICE_TYPE_CHORE): vol.In([DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE]),
})


class ChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)
        return self.async_show_form(step_id="user", data_schema=DEVICE_SCHEMA)

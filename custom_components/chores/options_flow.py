import voluptuous as vol
from datetime import datetime, timedelta
from homeassistant import config_entries
from homeassistant.util.dt import utcnow
from .const import DOMAIN, DEVICE_TYPE_CHORE, DEFAULT_POINTS, DEFAULT_DAYS

class HouseholdChoresOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        device_type = self.config_entry.data.get("device_type")

        options = self.config_entry.options
        now = utcnow()

        schema = {}
        if device_type == DEVICE_TYPE_CHORE:
            schema = vol.Schema({
                vol.Required("days", default=options.get("days", DEFAULT_DAYS)): vol.All(int, vol.Range(min=1, max=365)),
                vol.Required("points", default=options.get("points", DEFAULT_POINTS)): vol.All(int, vol.Range(min=0, max=20)),
                vol.Required("last_done_date", default=options.get("last_done_date", now)): str,
                vol.Required("next_due_date", default=options.get("next_due_date", now + timedelta(days=7))): str,
                vol.Optional("last_done_by", default=options.get("last_done_by", "")): str,
            })
        else:  # Score device
            schema = vol.Schema({
                vol.Required("points", default=options.get("points", 0)): vol.All(int, vol.Range(min=0, max=999)),
            })

        return self.async_show_form(step_id="init", data_schema=schema)

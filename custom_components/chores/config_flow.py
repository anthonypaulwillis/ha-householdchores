import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE, ATTR_POINTS, ATTR_DAYS, ATTR_LAST_DONE_DATE, ATTR_NEXT_DUE_DATE
from datetime import datetime, timedelta

DEVICE_TYPES = [DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE]

@config_entries.HANDLERS.register(DOMAIN)
class ChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data={
                "name": user_input["name"],
                "device_type": user_input["device_type"]
            }, options={
                ATTR_POINTS: user_input.get(ATTR_POINTS, 5),
                ATTR_DAYS: user_input.get(ATTR_DAYS, 7),
                ATTR_LAST_DONE_DATE: (datetime.utcnow()).isoformat(),
                ATTR_NEXT_DUE_DATE: (datetime.utcnow() + timedelta(days=user_input.get(ATTR_DAYS,7))).isoformat()
            })

        data_schema = vol.Schema({
            vol.Required("name"): str,
            vol.Required("device_type", default=DEVICE_TYPE_CHORE): vol.In(DEVICE_TYPES),
            vol.Optional(ATTR_POINTS, default=5): vol.All(int, vol.Range(min=0, max=20)),
            vol.Optional(ATTR_DAYS, default=7): vol.All(int, vol.Range(min=0, max=365)),
        })

        return self.async_show_form(step_id="user", data_schema=data_schema)

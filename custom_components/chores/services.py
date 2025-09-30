from homeassistant.core import HomeAssistant
from .const import DOMAIN

SERVICE_SET_VALUE = "set_value"

def async_register_services(hass: HomeAssistant):
    """Register services for Chores integration."""

    async def handle_set_value(call):
        chore_name = call.data["chore"]
        field = call.data["field"]
        value = call.data["value"]

        # Find entity in all entries
        for entry in hass.data[DOMAIN].values():
            for entity in entry.get("entities", []):
                if entity._chore_name == chore_name and entity._field == field:
                    entity.update_value(value)

    hass.services.async_register(DOMAIN, SERVICE_SET_VALUE, handle_set_value)

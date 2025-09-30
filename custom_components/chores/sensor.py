from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    ATTR_LAST_DAYS_OVERDUE,
)
from .entity import ChoresEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    # Only Chores have sensors (read-only values)
    if hasattr(device, "last_days_overdue"):
        entities.append(ChoresSensor(device, ATTR_LAST_DAYS_OVERDUE, "Last Days Overdue", entry.entry_id))

    async_add_entities(entities, True)


class ChoresSensor(ChoresEntity, SensorEntity):
    def __init__(self, device, attr, name_suffix, entry_id):
        super().__init__(device, attr, name_suffix, entry_id)

    @property
    def native_value(self):
        return getattr(self._device, self._attr)

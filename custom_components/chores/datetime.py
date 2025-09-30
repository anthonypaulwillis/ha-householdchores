from homeassistant.components.datetime import DateTimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_LATE_DONE_DATE, ATTR_NEXT_DUE_DATE
from .entity import ChoresEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    # Only Chores have date fields
    if hasattr(device, "late_done_date"):
        entities.append(ChoresDateTime(device, ATTR_LATE_DONE_DATE, "Late Done Date", entry.entry_id))
    if hasattr(device, "next_due_date"):
        entities.append(ChoresDateTime(device, ATTR_NEXT_DUE_DATE, "Next Due Date", entry.entry_id))

    async_add_entities(entities, True)


class ChoresDateTime(ChoresEntity, DateTimeEntity):
    def __init__(self, device, attr, name_suffix, entry_id):
        super().__init__(device, attr, name_suffix, entry_id)

    @property
    def native_value(self):
        return getattr(self._device, self._attr)

    async def async_set_value(self, value):
        setattr(self._device, self._attr, value)
        self.async_write_ha_state()

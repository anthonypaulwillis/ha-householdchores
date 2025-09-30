from homeassistant.components.datetime import DateTimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_LATE_DONE_DATE, ATTR_NEXT_DUE_DATE
from .entity import ChoresEntity

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    if hass.data[DOMAIN][entry.entry_id].get("datetime_entities_added"):
        return

    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    # Next Due Date
    if hasattr(device, "next_due_date"):
        next_due = ChoresDateTime(device, ATTR_NEXT_DUE_DATE, "Next Due Date", entry.entry_id)
        entities.append(next_due)
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][next_due.entity_id] = next_due

    # Last Done Date
    if hasattr(device, "late_done_date"):
        last_done = ChoresDateTime(device, ATTR_LATE_DONE_DATE, "Last Done Date", entry.entry_id)
        entities.append(last_done)
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][last_done.entity_id] = last_done

    async_add_entities(entities, True)
    hass.data[DOMAIN][entry.entry_id]["datetime_entities_added"] = True


class ChoresDateTime(ChoresEntity, DateTimeEntity):
    @property
    def native_value(self):
        return getattr(self._device, self._attr)

    async def async_set_value(self, value):
        setattr(self._device, self._attr, value)
        self.async_write_ha_state()

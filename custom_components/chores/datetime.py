from homeassistant.components.datetime import DatetimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
from .entity import ChoresEntity

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    if hasattr(device, "last_done_date"):
        last_done_entity = ChoresDatetimeEntity(device, "last_done_date", "Last Done", entry.entry_id)
        entities.append(last_done_entity)
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][last_done_entity.entity_id] = last_done_entity

    if hasattr(device, "next_due_date"):
        next_due_entity = ChoresDatetimeEntity(device, "next_due_date", "Next Due", entry.entry_id)
        entities.append(next_due_entity)
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][next_due_entity.entity_id] = next_due_entity

    async_add_entities(entities, True)

class ChoresDatetimeEntity(ChoresEntity, DatetimeEntity):
    @property
    def native_value(self):
        return getattr(self._device, self._attr_name)

    async def async_set_native_value(self, value):
        await super().async_set_native_value(value)

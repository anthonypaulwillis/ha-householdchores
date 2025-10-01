from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, "ATTR_LAST_DONE_BY"
from .entity import ChoresEntity

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    if hasattr(device, "last_done_by"):
        last_by_entity = ChoresTextEntity(device, "last_done_by", "Last Done By", entry.entry_id)
        entities.append(last_by_entity)
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][last_by_entity.entity_id] = last_by_entity

    async_add_entities(entities, True)

class ChoresTextEntity(ChoresEntity, TextEntity):
    @property
    def native_value(self):
        return getattr(self._device, self._attr_name, "")

    async def async_set_value(self, value):
        setattr(self._device, self._attr_name, value)
        if hasattr(self._device, "status_sensor_entity") and self._device.status_sensor_entity:
            self._device.status_sensor_entity.async_write_ha_state()
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            setattr(self._device, self._attr_name, last_state.state)

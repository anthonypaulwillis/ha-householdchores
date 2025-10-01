from homeassistant.components.datetime import DatetimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import parse_datetime
from .const import DOMAIN, ATTR_NEXT_DUE_DATE, ATTR_LAST_DONE_DATE
from .entity import ChoresEntity

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    if hasattr(device, "next_due_date"):
        next_entity = ChoresDatetimeEntity(device, ATTR_NEXT_DUE_DATE, "Next Due Date", entry.entry_id)
        entities.append(next_entity)
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][next_entity.entity_id] = next_entity

    if hasattr(device, "last_done_date"):
        last_entity = ChoresDatetimeEntity(device, ATTR_LAST_DONE_DATE, "Last Done Date", entry.entry_id)
        entities.append(last_entity)
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][last_entity.entity_id] = last_entity

    async_add_entities(entities, True)


class ChoresDatetimeEntity(ChoresEntity, DatetimeEntity):
    def __init__(self, device, attr_name, name, entry_id):
        super().__init__(device, attr_name, name, entry_id)

    @property
    def native_value(self):
        return getattr(self._device, self._attr_name)

    async def async_set_native_value(self, value):
        setattr(self._device, self._attr_name, value)
        if hasattr(self._device, "status_sensor_entity") and self._device.status_sensor_entity:
            self._device.status_sensor_entity.async_write_ha_state()
        await self._persist_state()
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            setattr(self._device, self._attr_name, parse_datetime(last_state.state))

    async def _persist_state(self):
        entry = self.hass.data[DOMAIN][self._entry_id]["entry"]
        from ..__init__ import persist_device_state
        await persist_device_state(entry, self._device)

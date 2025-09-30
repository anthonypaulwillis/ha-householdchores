from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_POINTS, ATTR_DAYS
from .entity import ChoresEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    if hass.data[DOMAIN][entry.entry_id].get("entities_added"):
        return

    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    entities.append(ChoresNumber(device, ATTR_POINTS, "Points", entry.entry_id))

    if hasattr(device, "days"):
        entities.append(ChoresNumber(device, ATTR_DAYS, "Days", entry.entry_id))

    for e in entities:
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][e.entity_id] = e

    async_add_entities(entities, True)


class ChoresNumber(ChoresEntity, NumberEntity):
    @property
    def native_value(self):
        return getattr(self._device, self._attr)

    async def async_set_native_value(self, value: float):
        setattr(self._device, self._attr, int(value))
        self.async_write_ha_state()

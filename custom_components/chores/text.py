from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_LAST_DONE_BY
from .entity import ChoresEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    # Only Chores have Last Done By
    if hasattr(device, "last_done_by"):
        entities.append(ChoresText(device, ATTR_LAST_DONE_BY, "Last Done By", entry.entry_id))

    async_add_entities(entities, True)


class ChoresText(ChoresEntity, TextEntity):
    def __init__(self, device, attr, name_suffix, entry_id):
        super().__init__(device, attr, name_suffix, entry_id)

    @property
    def native_value(self):
        return getattr(self._device, self._attr)

    async def async_set_value(self, value: str):
        setattr(self._device, self._attr, value)
        self.async_write_ha_state()

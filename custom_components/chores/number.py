from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_POINTS, ATTR_DAYS
from .entity import ChoresEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    # Both Chore and Score devices have points
    entities.append(ChoresNumber(device, ATTR_POINTS, "Points", entry.entry_id))

    # Only Chores have days
    if hasattr(device, "days"):
        entities.append(ChoresNumber(device, ATTR_DAYS, "Days", entry.entry_id))

    async_add_entities(entities, True)


class ChoresNumber(ChoresEntity, NumberEntity):
    def __init__(self, device, attr, name_suffix, entry_id):
        super().__init__(device, attr, name_suffix, entry_id)

    @property
    def native_value(self):
        return getattr(self._device, self._attr)

    async def async_set_native_value(self, value: float):
        setattr(self._device, self._attr, int(value))
        self.async_write_ha_state()

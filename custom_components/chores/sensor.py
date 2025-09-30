from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_TITLE, CONF_TYPE, DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE


class BaseFieldSensor(SensorEntity):
    """Base sensor for Chores integration."""

    def __init__(self, device_name: str, field: str, value, device_type: str, entry_id: str):
        self._device_name = device_name
        self._field = field
        self._device_type = device_type
        self._entry_id = entry_id

        self._attr_name = f"{device_name} {field.capitalize()}"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{field}"
        self._attr_native_value = value

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": self._device_name,
            "manufacturer": "Household",
            "model": self._device_type.capitalize(),
        }

    @property
    def native_value(self):
        return self._attr_native_value

    async def async_set_value(self, value):
        self._attr_native_value = value
        self.async_write_ha_state()


def create_entities(device_name: str, device_type: str, entry_id: str):
    """Return the correct set of entities based on device type."""
    entities = []

    if device_type == DEVICE_TYPE_CHORE:
        for field, default in [
            ("next", None),
            ("last", None),
            ("by", None),
            ("overdue", 0),
            ("points", 0),
            ("days", 0),
        ]:
            entities.append(BaseFieldSensor(device_name, field, default, device_type, entry_id))

    elif device_type == DEVICE_TYPE_SCORE:
        for field, default in [
            ("points", 0),
        ]:
            entities.append(BaseFieldSensor(device_name, field, default, device_type, entry_id))

    return entities


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up entities when a config entry is added."""
    title = entry.data[CONF_TITLE]
    device_type = entry.data[CONF_TYPE]

    entities = create_entities(title, device_type, entry.entry_id)
    async_add_entities(entities)

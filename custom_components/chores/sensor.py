from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE


class BaseFieldSensor(SensorEntity):
    """Base sensor for Chores integration."""

    def __init__(self, device_name: str, field: str, value, device_type: str):
        self._device_name = device_name
        self._field = field
        self._device_type = device_type
        self._attr_name = f"{device_name} {field.capitalize()}"
        self._attr_unique_id = f"{DOMAIN}_{device_type}_{device_name}_{field}"
        self._attr_native_value = value

    @property
    def native_value(self):
        return self._attr_native_value

    async def async_set_value(self, value):
        self._attr_native_value = value
        self.async_write_ha_state()


def create_entities(device_name: str, device_type: str):
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
            entities.append(BaseFieldSensor(device_name, field, default, device_type))

    elif device_type == DEVICE_TYPE_SCORE:
        for field, default in [
            ("points", 0),
        ]:
            entities.append(BaseFieldSensor(device_name, field, default, device_type))

    return entities

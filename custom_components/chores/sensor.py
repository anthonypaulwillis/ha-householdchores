from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

class ChoreFieldSensor(SensorEntity):
    """A sensor entity for a Chore field."""

    def __init__(self, chore_name: str, field: str, value):
        self._chore_name = chore_name
        self._field = field
        self._attr_name = f"{chore_name} {field.capitalize()}"
        self._attr_unique_id = f"{DOMAIN}_{chore_name}_{field}"
        self._attr_native_value = value

    @property
    def native_value(self):
        return self._attr_native_value

    async def async_set_value(self, value):
        self._attr_native_value = value
        self.async_write_ha_state()


class ScoreFieldSensor(SensorEntity):
    """A sensor entity for a Score field."""

    def __init__(self, user_name: str, field: str, value):
        self._user_name = user_name
        self._field = field
        self._attr_name = f"{user_name} {field.capitalize()}"
        self._attr_unique_id = f"{DOMAIN}_score_{user_name}_{field}"
        self._attr_native_value = value

    @property
    def native_value(self):
        return self._attr_native_value

    async def async_set_value(self, value):
        self._attr_native_value = value
        self.async_write_ha_state()

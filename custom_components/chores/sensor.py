from __future__ import annotations
import datetime
import json

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_TITLE, ATTR_NEXT, ATTR_LAST, ATTR_BY, ATTR_LAST_OVERDUE, ATTR_NOTIFY, ATTR_POINTS, ATTR_DAYS, ATTR_WHO_NOTIFY


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
):
    """Set up sensors for a chore entry."""
    title = entry.data[CONF_TITLE]
    sensors = []

    # Create one entity per field
    sensors.append(ChoreFieldSensor(title, ATTR_NEXT))
    sensors.append(ChoreFieldSensor(title, ATTR_LAST))
    sensors.append(ChoreFieldSensor(title, ATTR_BY))
    sensors.append(ChoreFieldSensor(title, ATTR_LAST_OVERDUE))
    sensors.append(ChoreFieldSensor(title, ATTR_NOTIFY))
    sensors.append(ChoreFieldSensor(title, ATTR_POINTS))
    sensors.append(ChoreFieldSensor(title, ATTR_DAYS))
    sensors.append(ChoreFieldSensor(title, ATTR_WHO_NOTIFY))

    async_add_entities(sensors)


class ChoreFieldSensor(SensorEntity):
    """Sensor representing a single field of a Chore."""

    def __init__(self, chore_name: str, field: str):
        self._chore_name = chore_name
        self._field = field
        self._attr_name = f"{chore_name} {field}"
        self._attr_unique_id = f"{chore_name.lower().replace(' ','_')}_{field}"
        self._state = STATE_UNKNOWN
        # Store values here; in future you can add JSON/state update logic
        self._value = None

    @property
    def state(self):
        return self._value if self._value is not None else STATE_UNKNOWN

    @property
    def extra_state_attributes(self):
        return {
            "chore": self._chore_name,
            "field": self._field
        }

    def update_value(self, value):
        """Set the value for this entity."""
        self._value = value
        self.async_write_ha_state()

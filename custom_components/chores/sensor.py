from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, CONF_TITLE, ATTR_NEXT, ATTR_LAST, ATTR_BY, ATTR_LAST_OVERDUE, ATTR_NOTIFY, ATTR_POINTS, ATTR_DAYS, ATTR_WHO_NOTIFY

FIELD_LIST = [
    ATTR_NEXT, ATTR_LAST, ATTR_BY, ATTR_LAST_OVERDUE,
    ATTR_NOTIFY, ATTR_POINTS, ATTR_DAYS, ATTR_WHO_NOTIFY
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up sensors for a Chore entry."""
    title = entry.data[CONF_TITLE]
    sensors = []

    # Keep track of entities in hass.data for service updates
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {"entities": []})

    for field in FIELD_LIST:
        sensor = ChoreFieldSensor(title, field)
        sensors.append(sensor)
        hass.data[DOMAIN][entry.entry_id]["entities"].append(sensor)

    async_add_entities(sensors)

class ChoreFieldSensor(SensorEntity):
    """Sensor representing a single field of a Chore."""

    def __init__(self, chore_name: str, field: str):
        self._chore_name = chore_name
        self._field = field
        self._attr_name = f"{chore_name} {field}"
        self._attr_unique_id = f"{chore_name.lower().replace(' ','_')}_{field}"
        self._value = STATE_UNKNOWN

    @property
    def state(self):
        return self._value

    @property
    def extra_state_attributes(self):
        return {
            "chore": self._chore_name,
            "field": self._field
        }

    @property
    def device_info(self):
        """Group all entities under a single Chore device."""
        return {
            "identifiers": {(DOMAIN, self._chore_name.lower().replace(" ", "_"))},
            "name": self._chore_name,
            "manufacturer": "Household Chores",
            "model": "Chore Device",
        }

    def update_value(self, value):
        """Update the sensor value dynamically."""
        self._value = value
        self.async_write_ha_state()

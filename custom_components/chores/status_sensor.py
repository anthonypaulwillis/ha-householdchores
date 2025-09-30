from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from datetime import datetime, timedelta

from .const import DOMAIN, ATTR_NEXT_DUE_DATE, ATTR_LATE_DONE_DATE
from .entity import ChoresEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    if hasattr(device, "next_due_date") or hasattr(device, "late_done_date"):
        status_entity = ChoresStatusSensor(device, "status", "Status", entry.entry_id)
        entities.append(status_entity)
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][status_entity.entity_id] = status_entity

    async_add_entities(entities, True)


class ChoresStatusSensor(ChoresEntity, SensorEntity):
    """Status sensor for Chores."""

    @property
    def native_value(self):
        now = datetime.now()
        next_due = getattr(self._device, ATTR_NEXT_DUE_DATE, None)
        last_done = getattr(self._device, ATTR_LATE_DONE_DATE, None)

        if last_done and (now - last_done) < timedelta(minutes=10):
            return "recent"
        if next_due:
            if next_due < now:
                overdue_days = (now - next_due).days
                if overdue_days > 2:
                    return "overdue"
                else:
                    return "due"
            else:
                return "not due"
        return "unknown"

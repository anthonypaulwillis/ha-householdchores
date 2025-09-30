from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from datetime import datetime, timedelta

from .const import DOMAIN, ATTR_NEXT_DUE_DATE, ATTR_LATE_DONE_DATE, ATTR_STATUS
from .entity import ChoresEntity

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    if hass.data[DOMAIN][entry.entry_id].get("sensor_entities_added"):
        return

    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    # Status sensor first
    status = ChoresStatusSensor(device, ATTR_STATUS, "Status", entry.entry_id)
    entities.append(status)
    hass.data[DOMAIN][entry.entry_id]["device_entity_map"][status.entity_id] = status

    async_add_entities(entities, True)
    hass.data[DOMAIN][entry.entry_id]["sensor_entities_added"] = True


class ChoresStatusSensor(ChoresEntity, SensorEntity):
    @property
    def native_value(self):
        now = datetime.now()
        next_due = getattr(self._device, ATTR_NEXT_DUE_DATE, None)
        last_done = getattr(self._device, ATTR_LATE_DONE_DATE, None)

        status = "unknown"

        if last_done and (now - last_done) < timedelta(minutes=10):
            status = "recent"
        elif next_due:
            if next_due < now:
                overdue_days = (now - next_due).days
                if overdue_days > 2:
                    status = "overdue"
                else:
                    status = "due"
            else:
                status = "not due"

        self._device.status = status
        return status

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import utcnow
from datetime import timedelta

from .const import DOMAIN, ATTR_NEXT_DUE_DATE, ATTR_LAST_DONE_DATE, ATTR_STATUS
from .entity import ChoresEntity
from .device import ChoreDevice


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Chore status sensor for a device."""
    if hass.data[DOMAIN][entry.entry_id].get("sensor_entities_added"):
        return

    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    if isinstance(device, ChoreDevice):
        status_sensor = ChoresStatusSensor(device, ATTR_STATUS, "Status", entry.entry_id)
        entities.append(status_sensor)
        # Link sensor to device entity map
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][status_sensor.entity_id] = status_sensor

    async_add_entities(entities, True)
    hass.data[DOMAIN][entry.entry_id]["sensor_entities_added"] = True


class ChoresStatusSensor(ChoresEntity, SensorEntity):
    """Reactive Status sensor for Chore devices."""

    def __init__(self, device: ChoreDevice, attr_name: str, name: str, entry_id: str):
        super().__init__(device, attr_name, name, entry_id)
        # Make the sensor known to the device for reactive updates
        self._device.status_sensor_entity = self

    @property
    def native_value(self):
        """Return the current status based on Chore device datetimes."""
        self._device.update_status()
        return self._device.status

    @property
    def should_poll(self):
        """No polling needed; updates are triggered reactively."""
        return False

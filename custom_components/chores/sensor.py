from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, ATTR_STATUS
from .entity import ChoresEntity
from .device import ChoreDevice

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    if hass.data[DOMAIN][entry.entry_id].get("sensor_entities_added"):
        return

    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    if isinstance(device, ChoreDevice):
        status_sensor = ChoresStatusSensor(device, ATTR_STATUS, "Status", entry.entry_id)
        entities.append(status_sensor)
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][status_sensor.entity_id] = status_sensor

    async_add_entities(entities, True)
    hass.data[DOMAIN][entry.entry_id]["sensor_entities_added"] = True

class ChoresStatusSensor(ChoresEntity, SensorEntity):
    def __init__(self, device, attr_name, name, entry_id):
        super().__init__(device, attr_name, name, entry_id)
        self._device.status_sensor_entity = self

    @property
    def native_value(self):
        self._device.update_status()
        return self._device.status

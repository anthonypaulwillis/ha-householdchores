from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import utcnow
from datetime import timedelta
from .const import DOMAIN
from .device import ChoreDevice

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    device = hass.data[DOMAIN][entry.entry_id]["device"]

    if isinstance(device, ChoreDevice):
        entity = ChoreStatusSensor(device, entry.entry_id)
        async_add_entities([entity], True)


class ChoreStatusSensor(SensorEntity):
    def __init__(self, device: ChoreDevice, entry_id: str):
        self._device = device
        self._attr_unique_id = f"{entry_id}_status"
        self._attr_name = f"{device.name} Status"

    @property
    def native_value(self):
        self._device.update_status()
        return self._device.status

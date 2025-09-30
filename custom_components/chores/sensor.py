from homeassistant.components.sensor import SensorEntity
from .entity import ChoresEntity

class ChoresSensor(ChoresEntity, SensorEntity):
    @property
    def native_value(self):
        return getattr(self._device, self._attr)

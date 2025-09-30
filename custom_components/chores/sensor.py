from homeassistant.components.sensor import SensorEntity
from .entity import ChoresEntity

class ChoresSensor(ChoresEntity, SensorEntity):
    def __init__(self, device, attr, name_suffix, entry_id):
        super().__init__(device, attr, name_suffix, entry_id)

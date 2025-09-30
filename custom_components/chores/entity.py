from homeassistant.helpers.entity import Entity
from .const import DOMAIN

class ChoresEntity(Entity):
    def __init__(self, device, attr, name_suffix, entry_id):
        self._device = device
        self._attr = attr
        self._attr_name = f"{device.name} {name_suffix}"
        self._entry_id = entry_id

    @property
    def unique_id(self):
        return f"{self._device.name.lower()}_{self._attr}"

    @property
    def name(self):
        return self._attr_name

    @property
    def available(self):
        return True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device.name)},   # unique per device
            "name": self._device.name,
            "manufacturer": "Household Chores",
            "model": self._device.__class__.__name__,       # shows ChoreDevice or ScoreDevice
            "entry_type": None,
        }

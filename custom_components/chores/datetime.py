from homeassistant.components.datetime import DateTimeEntity
from .entity import ChoresEntity

class ChoresDateTime(ChoresEntity, DateTimeEntity):
  @property
  def native_value(self):
    return getattr(self._device, self._attr)

  async def async_set_value(self, value):
    setattr(self._device, self._attr, value)
    self.async_write_ha_state()

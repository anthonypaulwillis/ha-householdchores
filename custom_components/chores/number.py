from homeassistant.components.number import NumberEntity
from .entity import ChoresEntity

class ChoresNumber(ChoresEntity, NumberEntity):
  @property
  def native_value(self):
    return getattr(self._device, self._attr)
  
  async def async_set_native_value(self, value: float):
    setattr(self._device, self._attr, value)
    self.async_write_ha_state()

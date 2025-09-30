from homeassistant.components.text import TextEntity
from .entity import ChoresEntity

class ChoresText(ChoresEntity, TextEntity):
  @property
  def native_value(self):
    return getattr(self._device, self._attr)

async def async_set_value(self, value: str):
  setattr(self._device, self._attr, value)
  self.async_write_ha_state()

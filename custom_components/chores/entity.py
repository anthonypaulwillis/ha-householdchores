from homeassistant.helpers.entity import Entity

class ChoresEntity(Entity):
  def __init__(self, device, attr, name_suffix):
    self._device = device
    self._attr = attr
    self._attr_name = f"{device.name} {name_suffix}"

  @property
  def unique_id(self):
    return f"{self._device.name.lower()}_{self._attr}"
  
  @property
  def name(self):
    return self._attr_name
  
  @property
  def available(self):
    return True

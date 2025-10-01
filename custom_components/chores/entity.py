from homeassistant.helpers.entity import RestoreEntity

class ChoresEntity(RestoreEntity):
    """Base entity for Chores integration."""

    def __init__(self, device, attr_name, name, entry_id):
        self._device = device
        self._attr_name = attr_name
        self._entry_id = entry_id
        self._attr_name_friendly = name

    @property
    def name(self):
        return f"{self._device.name} {self._attr_name_friendly}"

    @property
    def unique_id(self):
        return f"{self._device.device_id}_{self._attr_name}"

    async def async_added_to_hass(self):
        """Restore state on restart."""
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            # Convert appropriately
            current_value = last_state.state
            # Detect type from existing attribute
            attr = getattr(self._device, self._attr_name, None)
            if isinstance(attr, int):
                current_value = int(current_value)
            elif isinstance(attr, float):
                current_value = float(current_value)
            # datetime parsing is handled in datetime.py
            setattr(self._device, self._attr_name, current_value)

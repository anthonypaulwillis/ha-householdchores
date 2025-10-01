from homeassistant.helpers.entity import RestoreEntity
from homeassistant.core import callback

class ChoresEntity(RestoreEntity):
    """Base entity for Chores integration with state restoration."""

    def __init__(self, device, attr_name: str, friendly_name: str, entry_id: str):
        self._device = device
        self._attr_name = attr_name
        self._friendly_name = friendly_name
        self._entry_id = entry_id

    @property
    def name(self):
        """Human-readable name for the entity."""
        return f"{self._device.name} {self._friendly_name}"

    @property
    def unique_id(self):
        """Unique ID for the entity."""
        return f"{self._device.device_id}_{self._attr_name}"

    @property
    def should_poll(self):
        """Entities are reactive, do not poll."""
        return False

    async def async_added_to_hass(self):
        """Restore the last known state when entity is added."""
        await super().async_added_to_hass()

        # Attempt to restore last state from HA
        if last_state := await self.async_get_last_state():
            value = last_state.state
            attr = getattr(self._device, self._attr_name, None)

            # Attempt type conversion based on existing attribute
            if isinstance(attr, int):
                try:
                    value = int(value)
                except Exception:
                    value = attr
            elif isinstance(attr, float):
                try:
                    value = float(value)
                except Exception:
                    value = attr
            # datetime parsing is handled in datetime.py platform

            setattr(self._device, self._attr_name, value)

    @callback
    def async_update_device(self, value):
        """Update device attribute and trigger HA state update."""
        setattr(self._device, self._attr_name, value)
        self.async_write_ha_state()
        if hasattr(self._device, "status_sensor_entity") and self._device.status_sensor_entity:
            self._device.status_sensor_entity.async_write_ha_state()

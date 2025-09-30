from homeassistant.components.datetime import DateTimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_LATE_DONE_DATE, ATTR_NEXT_DUE_DATE
from .entity import ChoresEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Chore datetime entities (Next Due Date, Late Done Date)."""
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    # Late Done Date
    if hasattr(device, "late_done_date"):
        late_entity = ChoresDateTime(device, ATTR_LATE_DONE_DATE, "Late Done Date", entry.entry_id)
        entities.append(late_entity)
        # Register entity for service mapping
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][late_entity.entity_id] = late_entity

    # Next Due Date
    if hasattr(device, "next_due_date"):
        next_entity = ChoresDateTime(device, ATTR_NEXT_DUE_DATE, "Next Due Date", entry.entry_id)
        entities.append(next_entity)
        # Register entity for service mapping
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][next_entity.entity_id] = next_entity

    async_add_entities(entities, True)


class ChoresDateTime(ChoresEntity, DateTimeEntity):
    """Datetime entity for Chores Next/Late dates."""

    def __init__(self, device, attr, name_suffix, entry_id):
        super().__init__(device, attr, name_suffix, entry_id)

    @property
    def native_value(self):
        """Return current datetime value."""
        return getattr(self._device, self._attr)

    async def async_set_value(self, value):
        """Set datetime value (used by service)."""
        setattr(self._device, self._attr, value)
        self.async_write_ha_state()

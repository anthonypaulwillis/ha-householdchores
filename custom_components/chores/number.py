from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, ATTR_POINTS, ATTR_DAYS
from .entity import ChoresEntity

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []

    if hasattr(device, "points"):
        points_entity = ChoresNumberEntity(device, ATTR_POINTS, "Points", entry.entry_id, 0, 20)
        entities.append(points_entity)
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][points_entity.entity_id] = points_entity

    if hasattr(device, "days"):
        days_entity = ChoresNumberEntity(device, ATTR_DAYS, "Days", entry.entry_id, 0, 365)
        entities.append(days_entity)
        hass.data[DOMAIN][entry.entry_id]["device_entity_map"][days_entity.entity_id] = days_entity

    async_add_entities(entities, True)

class ChoresNumberEntity(ChoresEntity, NumberEntity):
    def __init__(self, device, attr_name, name, entry_id, min_value=0, max_value=100):
        super().__init

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.util.dt import parse_datetime, utcnow, now
from datetime import timedelta

from .const import DOMAIN, PLATFORMS, DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE
from .device import ChoreDevice, ScoreDevice

SERVICE_SET_VALUE = "set_value"
SERVICE_SET_DATETIME = "set_datetime"
SERVICE_COMPLETE_CHORE = "complete_chore"

async def async_setup(hass: HomeAssistant, config: ConfigType):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    return True

async def persist_device_state(entry, device):
    """Persist device state in Home Assistant."""
    entry_id = entry.entry_id
    if DOMAIN in entry.hass.data and entry_id in entry.hass.data[DOMAIN]:
        entry.hass.data[DOMAIN][entry_id]["device"] = device

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    device_type = entry.data.get("device_type")
    name = entry.data.get("name")

    if device_type == DEVICE_TYPE_CHORE:
        device = ChoreDevice(name)
    else:
        device = ScoreDevice(name)

    # Store device and map
    hass.data[DOMAIN][entry.entry_id] = {
        "device": device,
        "device_entity_map": {},
        "entry": entry,
    }

    # --- Service: set_value ---
    async def async_set_value_service(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        value = call.data["value"]

        entity_obj = hass.data[DOMAIN][entry.entry_id]["device_entity_map"].get(entity_id)
        if entity_obj:
            await entity_obj.async_set_native_value(value)
            entity_obj.async_write_ha_state()

    hass.services.async_register(DOMAIN, SERVICE_SET_VALUE, async_set_value_service)

    # --- Service: set_datetime ---
    async def async_set_datetime_service(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        value_str = call.data["value"]
        value = parse_datetime(value_str)

        entity_obj = hass.data[DOMAIN][entry.entry_id]["device_entity_map"].get(entity_id)
        if entity_obj:
            await entity_obj.async_set_native_value(value)
            entity_obj.async_write_ha_state()

    hass.services.async_register(DOMAIN, SERVICE_SET_DATETIME, async_set_datetime_service)

    # --- Service: complete_chore ---
    async def async_complete_chore_service(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        entity_obj = hass.data[DOMAIN][entry.entry_id]["device_entity_map"].get(entity_id)
        if entity_obj and entity_obj._device.device_type == DEVICE_TYPE_CHORE:
            chore_device = entity_obj._device
            now_time = utcnow()
            chore_device.last_done_date = now_time
            chore_device.next_due_date = now_time + timedelta(days=chore_device.days)
            if hasattr(chore_device, "status_sensor_entity") and chore_device.status_sensor_entity:
                chore_device.status_sensor_entity.async_write_ha_state()

            # Add points to matching Score device
            for eid, obj in hass.data[DOMAIN][entry.entry_id]["device_entity_map"].items():
                if obj._device.device_type == DEVICE_TYPE_SCORE and obj._device.name == call.context.user_name:
                    obj._device.points += chore_device.points
                    obj.async_write_ha_state()

            await persist_device_state(entry, chore_device)

    hass.services.async_register(DOMAIN, SERVICE_COMPLETE_CHORE, async_complete_chore_service)

    # Forward setups
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

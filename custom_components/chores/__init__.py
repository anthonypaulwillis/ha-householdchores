from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.util.dt import parse_datetime, utcnow
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

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    device_type = entry.data.get("device_type")
    name = entry.data.get("name")

    # Create device
    if device_type == DEVICE_TYPE_CHORE:
        device = ChoreDevice(name)
    else:
        device = ScoreDevice(name)

    # Auto-create Score devices for all users if Chore is added
    if device_type == DEVICE_TYPE_CHORE:
        # Attempt to create a Score device with same name as user if not exists
        existing_scores = [d._device.name for d in hass.data[DOMAIN].values() if getattr(d, "device_type", None) == DEVICE_TYPE_SCORE]
        if name not in existing_scores:
            score_device = ScoreDevice(name)
            entry_id_score = f"{entry.entry_id}_score_{name.replace(' ', '_')}"
            hass.data[DOMAIN][entry_id_score] = {
                "device": score_device,
                "device_entity_map": {},
                "entry": entry
            }

    # Store the device
    hass.data[DOMAIN][entry.entry_id] = {
        "device": device,
        "device_entity_map": {},
        "entry": entry,
    }

    # --- Service: set_value ---
    async def async_set_value_service(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        value = call.data["value"]
        entity_obj = None
        for entry_data in hass.data[DOMAIN].values():
            entity_obj = entry_data["device_entity_map"].get(entity_id)
            if entity_obj:
                break
        if entity_obj:
            await entity_obj.async_set_native_value(value)
            entity_obj.async_write_ha_state()

    hass.services.async_register(DOMAIN, SERVICE_SET_VALUE, async_set_value_service)

    # --- Service: set_datetime ---
    async def async_set_datetime_service(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        value = parse_datetime(call.data["value"])
        entity_obj = None
        for entry_data in hass.data[DOMAIN].values():
            entity_obj = entry_data["device_entity_map"].get(entity_id)
            if entity_obj:
                break
        if entity_obj:
            await entity_obj.async_set_native_value(value)
            entity_obj.async_write_ha_state()

    hass.services.async_register(DOMAIN, SERVICE_SET_DATETIME, async_set_datetime_service)

    # --- Service: complete_chore ---
    async def async_complete_chore_service(call):
        device = call.data["device"]
        if getattr(device, "device_type", None) != DEVICE_TYPE_CHORE:
            return
        chore_device = device
        now_time = utcnow()
        chore_device.last_done_date = now_time
        chore_device.next_due_date = now_time + timedelta(days=chore_device.days)
        if chore_device.status_sensor_entity:
            chore_device.status_sensor_entity.async_write_ha_state()

        # Find Score device for current user
        for entry_data in hass.data[DOMAIN].values():
            dev = entry_data["device"]
            if getattr(dev, "device_type", None) == DEVICE_TYPE_SCORE and dev.name == call.context.user_name:
                dev.points += chore_device.points
                if hasattr(dev, "status_sensor_entity") and dev.status_sensor_entity:
                    dev.status_sensor_entity.async_write_ha_state()

    hass.services.async_register(DOMAIN, SERVICE_COMPLETE_CHORE, async_complete_chore_service)

    # Forward setups
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

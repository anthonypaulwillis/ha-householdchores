from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.util.dt import parse_datetime, now as dt_now

from .const import DOMAIN, PLATFORMS, DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE
from .device import ChoreDevice, ScoreDevice

SERVICE_SET_DATETIME = "set_datetime"
SERVICE_SET_VALUE = "set_value"
SERVICE_COMPLETE_CHORE = "complete_chore"


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the Chores integration."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
        hass.data[DOMAIN]["score_devices_created"] = False
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a Chore or Score device from a config entry."""
    data = entry.data
    device_type = data.get("device_type")
    name = data.get("name")

    # Restore values if present in entry.data
    points = data.get("points", 5 if device_type == DEVICE_TYPE_CHORE else 0)
    days = data.get("days", 7)
    last_done_date = parse_datetime(data.get("last_done_date")) if data.get("last_done_date") else None
    next_due_date = parse_datetime(data.get("next_due_date")) if data.get("next_due_date") else None
    last_done_by = data.get("last_done_by", "")

    if device_type == DEVICE_TYPE_CHORE:
        device = ChoreDevice(name, points, days, last_done_date, next_due_date, last_done_by)
    else:
        device = ScoreDevice(name, points)

    hass.data[DOMAIN][entry.entry_id] = {
        "device": device,
        "device_entity_map": {},
        "entry": entry,
    }

    # --- Auto-create Score devices once ---
    if not hass.data[DOMAIN]["score_devices_created"]:
        users = await hass.auth.async_get_users()
        for user in users:
            # Skip if Score device for this user exists
            if any(
                isinstance(d["device"], ScoreDevice) and d["device"].name == user.name
                for d in hass.data[DOMAIN].values()
            ):
                continue
            sdev = ScoreDevice(user.name)
            fake_entry_id = f"auto_score_{user.id}"
            hass.data[DOMAIN][fake_entry_id] = {"device": sdev, "device_entity_map": {}, "entry": entry}
            await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        hass.data[DOMAIN]["score_devices_created"] = True

    # --- Services ---
    async def async_set_value_service(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        value = call.data["value"]

        entity_obj = hass.data[DOMAIN][entry.entry_id]["device_entity_map"].get(entity_id)
        if entity_obj:
            await entity_obj.async_set_value(value)
            entity_obj.async_write_ha_state()
            # Update Status sensor
            if hasattr(entity_obj.device, "status_sensor_entity") and entity_obj.device.status_sensor_entity:
                entity_obj.device.status_sensor_entity.async_write_ha_state()
            # Persist change
            await persist_device_state(entry, entity_obj.device)

    hass.services.async_register(DOMAIN, SERVICE_SET_VALUE, async_set_value_service)

    async def async_set_datetime_service(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        value_str = call.data["value"]
        value = parse_datetime(value_str)

        entity_obj = hass.data[DOMAIN][entry.entry_id]["device_entity_map"].get(entity_id)
        if entity_obj:
            await entity_obj.async_set_value(value)
            entity_obj.async_write_ha_state()
            # Update Status sensor
            if hasattr(entity_obj.device, "status_sensor_entity") and entity_obj.device.status_sensor_entity:
                entity_obj.device.status_sensor_entity.async_write_ha_state()
            # Persist change
            await persist_device_state(entry, entity_obj.device)

    hass.services.async_register(DOMAIN, SERVICE_SET_DATETIME, async_set_datetime_service)

    async def async_complete_chore_service(call):
        device_id = call.data.get("device_id")
        user_name = "Unknown"
        if call.context.user_id:
            user = await hass.auth.async_get_user(call.context.user_id)
            if user:
                user_name = user.name or user.id

        for data_entry in hass.data[DOMAIN].values():
            dev = data_entry["device"]
            if isinstance(dev, ChoreDevice) and getattr(dev, "device_id", None) == device_id:
                now = dt_now()
                dev.last_done_date = now
                dev.last_done_by = user_name
                if dev.days:
                    dev.next_due_date = now + timedelta(days=dev.days)
                dev.update_status()
                # Refresh all entities
                for entity in data_entry["device_entity_map"].values():
                    entity.async_write_ha_state()
                # Status sensor update
                if hasattr(dev, "status_sensor_entity") and dev.status_sensor_entity:
                    dev.status_sensor_entity.async_write_ha_state()
                # Add points to Score device
                for sdata in hass.data[DOMAIN].values():
                    sdev = sdata["device"]
                    if isinstance(sdev, ScoreDevice) and sdev.name == user_name:
                        sdev.points += dev.points
                        for entity in sdata["device_entity_map"].values():
                            entity.async_write_ha_state()
                        await persist_device_state(sdata["entry"], sdev)
                        break
                await persist_device_state(entry, dev)
                break

    hass.services.async_register(DOMAIN, SERVICE_COMPLETE_CHORE, async_complete_chore_service)

    # --- Forward to platforms ---
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def persist_device_state(entry: ConfigEntry, device):
    """Save current device state to the config entry."""
    data = dict(entry.data)
    if isinstance(device, ChoreDevice):
        data.update({
            "points": device.points,
            "days": device.days,
            "last_done_date": device.last_done_date.isoformat() if device.last_done_date else None,
            "next_due_date": device.next_due_date.isoformat() if device.next_due_date else None,
            "last_done_by": device.last_done_by,
        })
    elif isinstance(device, ScoreDevice):
        data.update({"points": device.points})
    await entry.async_update(data)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry and its platforms."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

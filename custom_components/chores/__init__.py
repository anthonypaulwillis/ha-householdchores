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
    """Set up the Chores integration and create Score devices for all HA users."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Create Score devices for all HA users if they don't already exist
    users = await hass.auth.async_get_users()
    for user in users:
        if not any(
            isinstance(d["device"], ScoreDevice) and d["device"].name == user.name
            for d in hass.data[DOMAIN].values()
        ):
            sdev = ScoreDevice(user.name)
            fake_entry_id = f"auto_score_{user.id}"
            hass.data[DOMAIN][fake_entry_id] = {"device": sdev, "device_entity_map": {}}

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a Chore or Score device from a config entry."""
    device_type = entry.data.get("device_type")
    name = entry.data.get("name")

    if device_type == DEVICE_TYPE_CHORE:
        device = ChoreDevice(name)
    else:
        device = ScoreDevice(name)

    hass.data[DOMAIN][entry.entry_id] = {
        "device": device,
        "device_entity_map": {},
    }

    # --- Service: set_value ---
    async def async_set_value_service(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        value = call.data["value"]

        entity_obj = hass.data[DOMAIN][entry.entry_id]["device_entity_map"].get(entity_id)
        if entity_obj:
            await entity_obj.async_set_value(value)
            entity_obj.async_write_ha_state()

    hass.services.async_register(DOMAIN, SERVICE_SET_VALUE, async_set_value_service)

    # --- Service: set_datetime ---
    async def async_set_datetime_service(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        value_str = call.data["value"]
        value = parse_datetime(value_str)

        entity_obj = hass.data[DOMAIN][entry.entry_id]["device_entity_map"].get(entity_id)
        if entity_obj:
            await entity_obj.async_set_value(value)
            entity_obj.async_write_ha_state()

    hass.services.async_register(DOMAIN, SERVICE_SET_DATETIME, async_set_datetime_service)

    # --- Service: complete_chore ---
    async def async_complete_chore_service(call):
        device_id = call.data.get("device_id")

        # Detect the user running the service
        user_name = "Unknown"
        if call.context.user_id:
            user = await hass.auth.async_get_user(call.context.user_id)
            if user:
                user_name = user.name or user.id

        # Find the Chore device
        for data in hass.data[DOMAIN].values():
            dev = data["device"]
            if isinstance(dev, ChoreDevice) and getattr(dev, "device_id", None) == device_id:
                now = dt_now()
                dev.last_done_date = now
                dev.last_done_by = user_name
                if dev.days:
                    dev.next_due_date = now + timedelta(days=dev.days)

                # Update status
                dev.update_status()

                # Refresh all linked entities
                for entity in data["device_entity_map"].values():
                    entity.async_write_ha_state()

                # Add points to user's Score device
                for sdata in hass.data[DOMAIN].values():
                    sdev = sdata["device"]
                    if isinstance(sdev, ScoreDevice) and sdev.name == user_name:
                        sdev.points += dev.points
                        for entity in sdata["device_entity_map"].values():
                            entity.async_write_ha_state()
                        break
                break

    hass.services.async_register(DOMAIN, SERVICE_COMPLETE_CHORE, async_complete_chore_service)

    # Forward to platform setups (sensor, number, text, datetime)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry and its platforms."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

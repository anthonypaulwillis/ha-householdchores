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
    """Set up the Chores integration from configuration.yaml (not used in this case)."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
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
        "device_entity_map": {},  # Populated later by platforms
    }

    # --- Service: set_value ---
    async def async_set_value_service(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        value = call.data["value"]

        entity_obj = hass.data[DOMAIN][entry.entry_id]["device_entity_map"].get(entity_id)
        if entity_obj:
            await entity_obj.async_set_value(value)
            entity_obj.async_write_ha_state()

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_VALUE,
        async_set_value_service
    )

    # --- Service: set_datetime ---
    async def async_set_datetime_service(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        value_str = call.data["value"]
        value = parse_datetime(value_str)

        entity_obj = hass.data[DOMAIN][entry.entry_id]["device_entity_map"].get(entity_id)
        if entity_obj:
            await entity_obj.async_set_value(value)
            entity_obj.async_write_ha_state()

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_DATETIME,
        async_set_datetime_service
    )

    # --- Service: complete_chore ---
    async def async_complete_chore_service(call):
        device_id = call.data.get("device_id")

        # Search all registered devices for a matching ChoreDevice
        for data in hass.data[DOMAIN].values():
            dev = data["device"]
            if isinstance(dev, ChoreDevice) and getattr(dev, "device_id", None) == device_id:
                now = dt_now()
                dev.last_done_date = now
                if dev.days:
                    dev.next_due_date = now + timedelta(days=dev.days)

                # Update status immediately
                dev.update_status()

                # Refresh all linked entities
                for entity in data["device_entity_map"].values():
                    entity.async_write_ha_state()
                break

    hass.services.async_register(
        DOMAIN,
        SERVICE_COMPLETE_CHORE,
        async_complete_chore_service
    )

    # Forward to platform setups
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry and its platforms."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

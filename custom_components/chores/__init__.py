from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.util.dt import parse_datetime

from .const import DOMAIN, PLATFORMS, DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE
from .device import ChoreDevice, ScoreDevice

SERVICE_SET_DATETIME = "set_datetime"
SERVICE_SET_VALUE = "set_value"


async def async_setup(hass: HomeAssistant, config: ConfigType):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
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

    # Forward setups
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

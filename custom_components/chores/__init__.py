from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.util.dt import parse_datetime, utcnow
from datetime import timedelta

from .const import DOMAIN, PLATFORMS, DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE
from .device import ChoreDevice, ScoreDevice

SERVICE_SET_VALUE = "set_value"
SERVICE_SET_DATETIME = "set_datetime"
SERVICE_COMPLETE_CHORE = "complete_chore"


async def async_setup(hass: HomeAssistant, config):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    device_type = entry.data.get("device_type")
    name = entry.data.get("name")

    if device_type == DEVICE_TYPE_CHORE:
        device = ChoreDevice(name, entry.options)
    else:
        device = ScoreDevice(name, entry.options)

    hass.data[DOMAIN][entry.entry_id] = {"device": device}

    # --- Service: set_value ---
    async def async_set_value(call: ServiceCall):
        field = call.data.get("field")
        value = call.data.get("value")
        new_options = dict(entry.options)
        new_options[field] = value
        hass.config_entries.async_update_entry(entry, options=new_options)

    hass.services.async_register(DOMAIN, SERVICE_SET_VALUE, async_set_value)

    # --- Service: set_datetime ---
    async def async_set_datetime(call: ServiceCall):
        field = call.data.get("field")
        value_str = call.data.get("value")
        value = parse_datetime(value_str)
        new_options = dict(entry.options)
        new_options[field] = value
        hass.config_entries.async_update_entry(entry, options=new_options)

    hass.services.async_register(DOMAIN, SERVICE_SET_DATETIME, async_set_datetime)

    # --- Service: complete_chore ---
    async def async_complete_chore(call: ServiceCall):
        now = utcnow()
        new_options = dict(entry.options)
        new_options["last_done_date"] = now
        days = int(new_options.get("days", 7))
        new_options["next_due_date"] = now + timedelta(days=days)
        hass.config_entries.async_update_entry(entry, options=new_options)

    hass.services.async_register(DOMAIN, SERVICE_COMPLETE_CHORE, async_complete_chore)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

from . import device_action
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, CONF_TITLE, CONF_TYPE
from .sensor import create_entities
from .services import async_register_services

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Chores integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a Chore or Score device from a config entry."""
    title = entry.data[CONF_TITLE]
    device_type = entry.data[CONF_TYPE]

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"title": title, "type": device_type}

    # Register device in Device Registry
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer="Household",
        name=title,
        model=device_type.capitalize(),
    )

    # Register Chores services
    async_register_services(hass)

    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True

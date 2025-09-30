from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType


from .const import DOMAIN, PLATFORMS


async def async_setup(hass: HomeAssistant, config: ConfigType):
return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

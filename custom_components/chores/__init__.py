from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_TITLE
from .services import async_register_services
from .sensor import ChoreFieldSensor, ScoreFieldSensor

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Chores integration via YAML (optional)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Chores integration from a config entry."""
    title = entry.data[CONF_TITLE]

    # Initialize integration storage
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {
        "title": title,
        "entities": []
    })

    # Initialize Score device storage
    hass.data.setdefault("scores", {})

    # Register Chores services
    async_register_services(hass)

    # Forward to sensor platform to create Chore entities
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a Chore entry and its entities."""
    await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


# Optional helper to create Score devices programmatically
def create_score_device(hass: HomeAssistant, user_name: str):
    """Create a Score device for a user if it does not exist."""
    if user_name in hass.data["scores"]:
        return

    # Create entities for Score device
    title_entity = ScoreFieldSensor(user_name, "title", user_name)
    points_entity = ScoreFieldSensor(user_name, "points", 0)

    hass.data["scores"][user_name] = {
        "entities": [title_entity, points_entity]
    }

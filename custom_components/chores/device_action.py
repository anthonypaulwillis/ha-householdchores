from typing import List, Dict, Any
import voluptuous as vol

from homeassistant.const import CONF_ENTITY_ID
from homeassistant.helpers.typing import ConfigType
from homeassistant.core import HomeAssistant

from .const import DOMAIN

ACTION_DO_CHORE = "Do Chore"
ACTION_UPDATE_POINTS = "Update Points"
ACTION_UPDATE_DAYS = "Update Days"

ACTION_TYPES = [ACTION_DO_CHORE, ACTION_UPDATE_POINTS, ACTION_UPDATE_DAYS]

ACTION_SCHEMA_BASE = {
    vol.Required("type"): vol.In(ACTION_TYPES),
    vol.Required(CONF_ENTITY_ID): str,
}

UPDATE_POINTS_SCHEMA = vol.Schema({**ACTION_SCHEMA_BASE, vol.Required("points"): int})
UPDATE_DAYS_SCHEMA = vol.Schema({**ACTION_SCHEMA_BASE, vol.Required("days"): int})
DO_CHORE_SCHEMA = vol.Schema(ACTION_SCHEMA_BASE)


async def async_get_actions(hass: HomeAssistant, device_id: str) -> List[Dict[str, Any]]:
    """List device actions for a device."""
    actions = []
    for action_type in ACTION_TYPES:
        actions.append({"domain": DOMAIN, "type": action_type, "device_id": device_id})
    return actions


async def async_call_action_from_config(hass: HomeAssistant, config: ConfigType, variables: Dict[str, Any], context):
    """Execute a device action."""
    action_type = config["type"]
    entity_id = config[CONF_ENTITY_ID]

    if action_type == ACTION_DO_CHORE:
        await hass.services.async_call(DOMAIN, "do_chore", {"entity_id": entity_id}, context=context)

    elif action_type == ACTION_UPDATE_POINTS:
        points = config.get("points", 0)
        await hass.services.async_call(DOMAIN, "update_points", {"entity_id": entity_id, "points": points}, context=context)

    elif action_type == ACTION_UPDATE_DAYS:
        days = config.get("days", 0)
        await hass.services.async_call(DOMAIN, "update_days", {"entity_id": entity_id, "days": days}, context=context)

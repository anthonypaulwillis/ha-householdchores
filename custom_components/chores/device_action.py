from typing import List, Dict, Any
import voluptuous as vol

from homeassistant.const import CONF_TYPE, CONF_ENTITY_ID
from homeassistant.helpers.typing import ConfigType
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DEVICE_TYPE_CHORE, DEVICE_TYPE_SCORE

ACTION_DO_CHORE = "do_chore"
ACTION_UPDATE_POINTS = "update_points"
ACTION_UPDATE_DAYS = "update_days"

ACTION_TYPES = [ACTION_DO_CHORE, ACTION_UPDATE_POINTS, ACTION_UPDATE_DAYS]

ACTION_SCHEMA = vol.Schema(
    {
        vol.Required("type"): vol.In(ACTION_TYPES),
        vol.Required(CONF_ENTITY_ID): str,
    }
)


async def async_get_actions(hass: HomeAssistant, device_id: str) -> List[Dict[str, Any]]:
    """List device actions for a device."""
    actions = []

    # For simplicity, always expose all actions for any chores device
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
        await hass.services.async_call(DOMAIN, "update_points", {"entity_id": entity_id, "points": 0}, context=context)
    elif action_type == ACTION_UPDATE_DAYS:
        await hass.services.async_call(DOMAIN, "update_days", {"entity_id": entity_id, "days": 0}, context=context)

import voluptuous as vol
from typing import List, Dict, Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_ENTITY_ID

from .const import DOMAIN

ACTION_DO_CHORE = "Do Chore"
ACTION_UPDATE_POINTS = "Update Points"
ACTION_UPDATE_DAYS = "Update Days"

# This top-level schema is required by HA for validation
ACTION_SCHEMA = vol.Schema({
    vol.Required("type"): vol.In([ACTION_DO_CHORE, ACTION_UPDATE_POINTS, ACTION_UPDATE_DAYS]),
    vol.Required(CONF_ENTITY_ID): str,
    vol.Optional("points"): int,
    vol.Optional("days"): int,
})


async def async_get_actions(hass: HomeAssistant, device_id: str):
    """List device actions for a device."""
    actions = []
    for action_type in [ACTION_DO_CHORE, ACTION_UPDATE_POINTS, ACTION_UPDATE_DAYS]:
        actions.append({
            "type": action_type,
            "device_id": device_id
        })
    return actions


async def async_call_action_from_config(
    hass: HomeAssistant,
    config: ConfigType,
    variables: Dict[str, Any],
    context,
):
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

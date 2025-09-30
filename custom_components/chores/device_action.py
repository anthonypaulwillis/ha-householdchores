import voluptuous as vol
from typing import List, Dict, Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_ENTITY_ID

from .const import DOMAIN

ACTION_DO_CHORE = "do_chore"
ACTION_UPDATE_POINTS = "update_points"
ACTION_UPDATE_DAYS = "update_days"

# Action schema
ACTION_SCHEMA = vol.Schema({
    vol.Required("type"): vol.In([ACTION_DO_CHORE, ACTION_UPDATE_POINTS, ACTION_UPDATE_DAYS]),
    vol.Required("device_id"): str,
    vol.Optional(CONF_ENTITY_ID): str,
    vol.Optional("points"): int,
    vol.Optional("days"): int,
})

async def async_get_actions(hass: HomeAssistant, device_id: str) -> List[Dict[str, Any]]:
    """Return all actions available for a device."""
    return [
        {"type": ACTION_DO_CHORE, "device_id": device_id},
        {"type": ACTION_UPDATE_POINTS, "device_id": device_id},
        {"type": ACTION_UPDATE_DAYS, "device_id": device_id},
    ]

async def async_get_action_capabilities(hass: HomeAssistant, config: ConfigType) -> Dict[str, Any]:
    """Return fields for actions so UI can render them."""
    if config["type"] == ACTION_UPDATE_POINTS:
        return {
            "extra_fields": vol.Schema({
                vol.Required("points"): vol.Coerce(int),
            })
        }
    elif config["type"] == ACTION_UPDATE_DAYS:
        return {
            "extra_fields": vol.Schema({
                vol.Required("days"): vol.Coerce(int),
            })
        }
    return {"extra_fields": vol.Schema({})}

async def async_call_action_from_config(
    hass: HomeAssistant,
    config: ConfigType,
    variables: Dict[str, Any],
    context,
):
    """Execute a device action."""
    action_type = config["type"]
    entity_id = config.get(CONF_ENTITY_ID)

    if action_type == ACTION_DO_CHORE:
        await hass.services.async_call(DOMAIN, "do_chore", {"entity_id": entity_id}, context=context)
    elif action_type == ACTION_UPDATE_POINTS:
        await hass.services.async_call(
            DOMAIN, "update_points",
            {"entity_id": entity_id, "points": config["points"]},
            context=context
        )
    elif action_type == ACTION_UPDATE_DAYS:
        await hass.services.async_call(
            DOMAIN, "update_days",
            {"entity_id": entity_id, "days": config["days"]},
            context=context
        )

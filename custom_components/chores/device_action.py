import voluptuous as vol
from typing import List, Dict, Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_ENTITY_ID

from .const import DOMAIN

# Capitalized names for UI
ACTION_DO_CHORE = "Do Chore"
ACTION_UPDATE_POINTS = "Update Points"
ACTION_UPDATE_DAYS = "Update Days"

# Top-level schema required by HA
ACTION_SCHEMA = vol.Schema({
    vol.Required("type"): vol.In([ACTION_DO_CHORE, ACTION_UPDATE_POINTS, ACTION_UPDATE_DAYS]),
    vol.Optional(CONF_ENTITY_ID): str,  # optional because Do Chore will auto-select entity
    vol.Optional("points"): int,
    vol.Optional("days"): int,
})


async def async_get_actions(hass: HomeAssistant, device_id: str) -> List[Dict[str, Any]]:
    """List device actions for a device."""
    actions = []
    for action_type in [ACTION_DO_CHORE, ACTION_UPDATE_POINTS, ACTION_UPDATE_DAYS]:
        actions.append({
            "type": action_type,
            "device_id": device_id
        })
    return actions


async def async_get_action_capabilities(hass: HomeAssistant, config: ConfigType) -> Dict[str, Any]:
    """Return extra fields for an action so HA can render numeric input in UI."""
    action_type = config["type"]

    if action_type == ACTION_UPDATE_POINTS:
        return {"extra_fields": vol.Schema({vol.Required("points"): int})}
    elif action_type == ACTION_UPDATE_DAYS:
        return {"extra_fields": vol.Schema({vol.Required("days"): int})}
    else:
        # Do Chore: auto-select the entity, no extra fields
        return {"extra_fields": vol.Schema({})}


async def async_call_action_from_config(
    hass: HomeAssistant,
    config: ConfigType,
    variables: Dict[str, Any],
    context,
):
    """Execute a device action."""
    action_type = config["type"]
    device_id = config["device_id"]

    # Find the primary chore entity for this device
    # We assume the first entity of type 'next' belongs to the chore device
    entity_id = config.get(CONF_ENTITY_ID)
    if not entity_id and action_type == ACTION_DO_CHORE:
        # Look up all entities for this device
        dev_registry = await hass.helpers.device_registry.async_get_registry()
        entities = [
            e.entity_id for e in hass.states.async_entity_ids("sensor")
            if dev_registry.async_get_entity(e).device_id == device_id
        ]
        if entities:
            entity_id = entities[0]  # auto-pick first entity

    if action_type == ACTION_DO_CHORE:
        await hass.services.async_call(DOMAIN, "do_chore", {"entity_id": entity_id}, context=context)
    elif action_type == ACTION_UPDATE_POINTS:
        points = config.get("points", 0)
        await hass.services.async_call(DOMAIN, "update_points", {"entity_id": entity_id, "points": points}, context=context)
    elif action_type == ACTION_UPDATE_DAYS:
        days = config.get("days", 0)
        await hass.services.async_call(DOMAIN, "update_days", {"entity_id": entity_id, "days": days}, context=context)

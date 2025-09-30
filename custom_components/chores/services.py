from datetime import datetime, timedelta

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, Context
from homeassistant.helpers import entity_registry as er
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEVICE_TYPE_CHORE


SERVICE_DO_CHORE = "do_chore"
SERVICE_UPDATE_POINTS = "update_points"
SERVICE_UPDATE_DAYS = "update_days"

# Schemas for service validation
DO_CHORE_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
})

UPDATE_POINTS_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("points"): vol.Coerce(int),
})

UPDATE_DAYS_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("days"): vol.Coerce(int),
})


def async_register_services(hass: HomeAssistant):
    """Register services for the Chores integration."""

    async def async_do_chore(call: ServiceCall):
        """Handle Do Chore service."""
        entity_id = call.data["entity_id"]
        context: Context = call.context

        ent_reg = er.async_get(hass)
        entity_entry = ent_reg.async_get(entity_id)
        if not entity_entry:
            return

        # Get chore name from entity_id ("sensor.{title}_next" → title)
        chore_name = entity_entry.unique_id.split("_")[2]

        # Get user name if available
        user_name = context.user_id or "Unknown"

        now = datetime.now()

        # Update fields
        for suffix, value in [
            ("by", user_name),
            ("last", now.isoformat()),
        ]:
            target_entity = f"sensor.{chore_name}_{suffix}"
            state = hass.states.get(target_entity)
            if state:
                hass.states.async_set(target_entity, value, state.attributes)

        # Get days value
        days_entity = f"sensor.{chore_name}_days"
        days_state = hass.states.get(days_entity)
        days = int(days_state.state) if days_state and days_state.state.isdigit() else 0

        # Compute next timestamp
        next_time = now + timedelta(days=days)
        next_entity = f"sensor.{chore_name}_next"
        hass.states.async_set(next_entity, next_time.isoformat(), {})

        # Compute overdue (difference between now and previous next)
        overdue_entity = f"sensor.{chore_name}_overdue"
        if days_entity:
            overdue_days = (now - next_time).days
            hass.states.async_set(overdue_entity, overdue_days, {})

        # Add points to matching Score device
        points_entity = f"sensor.{chore_name}_points"
        points_state = hass.states.get(points_entity)
        points = int(points_state.state) if points_state and points_state.state.isdigit() else 0

        score_entity = f"sensor.{user_name}_points"
        score_state = hass.states.get(score_entity)
        if score_state:
            score_val = int(score_state.state) if score_state.state.isdigit() else 0
            hass.states.async_set(score_entity, score_val + points, {})

    async def async_update_points(call: ServiceCall):
        """Handle Update Points service."""
        entity_id = call.data["entity_id"]
        points = call.data["points"]

        state = hass.states.get(entity_id)
        if state:
            hass.states.async_set(entity_id, points, state.attributes)

    async def async_update_days(call: ServiceCall):
        """Handle Update Days service."""
        entity_id = call.data["entity_id"]
        days = call.data["days"]

        state = hass.states.get(entity_id)
        if state:
            hass.states.async_set(entity_id, days, state.attributes)

    # Register services
    hass.services.async_register(DOMAIN, SERVICE_DO_CHORE, async_do_chore, schema=DO_CHORE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_POINTS, async_update_points, schema=UPDATE_POINTS_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_DAYS, async_update_days, schema=UPDATE_DAYS_SCHEMA)

from homeassistant.core import HomeAssistant, ServiceCall
from .const import DOMAIN, ATTR_NEXT, ATTR_LAST, ATTR_BY, ATTR_OVERDUE, ATTR_POINTS, ATTR_DAYS

SERVICE_DO_CHORE = "do_chore"
SERVICE_UPDATE_POINTS = "update_points"
SERVICE_UPDATE_DAYS = "update_days"
SERVICE_SCORE_OVERRIDE = "score_override"

def async_register_services(hass: HomeAssistant):
    """Register Chores services."""

    async def handle_do_chore(call: ServiceCall):
        chore_name = call.data["chore"]
        user_name = call.data.get("user", "Unknown")
        from datetime import datetime, timedelta

        # Find the chore entry and entities
        for entry in hass.data[DOMAIN].values():
            for entity in entry.get("entities", []):
                if entity._chore_name != chore_name:
                    continue

                now = datetime.now()

                if entity._field == ATTR_BY:
                    entity.update_value(user_name)

                elif entity._field == ATTR_LAST:
                    entity.update_value(now.isoformat())

                elif entity._field == ATTR_NEXT:
                    # Find the days entity to calculate next
                    days_entity = next((e for e in entry["entities"] if e._field == ATTR_DAYS), None)
                    days = int(days_entity.state) if days_entity else 0
                    next_time = now + timedelta(days=days)
                    entity.update_value(next_time.isoformat())

                elif entity._field == ATTR_OVERDUE:
                    # Calculate overdue
                    next_entity = next((e for e in entry["entities"] if e._field == ATTR_NEXT), None)
                    if next_entity:
                        next_dt = datetime.fromisoformat(next_entity.state)
                        overdue_days = round((now - next_dt).total_seconds() / (60*60*24))
                        entity.update_value(overdue_days)

                elif entity._field == ATTR_POINTS:
                    points_entity = next((e for e in entry["entities"] if e._field == ATTR_POINTS), None)
                    # Will be used to update Score device later
                    points = int(points_entity.state) if points_entity else 0

        # Update Score device for this user
        score_entry = hass.data.get("scores", {}).get(user_name)
        if score_entry:
            score_points_entity = next((e for e in score_entry["entities"] if e._field == ATTR_POINTS), None)
            if score_points_entity:
                score_points_entity.update_value(
                    int(score_points_entity.state or 0) + points
                )

    async def handle_update_points(call: ServiceCall):
        chore_name = call.data["chore"]
        points_value = int(call.data["points"])

        for entry in hass.data[DOMAIN].values():
            for entity in entry.get("entities", []):
                if entity._chore_name == chore_name and entity._field == ATTR_POINTS:
                    entity.update_value(points_value)

    async def handle_update_days(call: ServiceCall):
        chore_name = call.data["chore"]
        days_value = int(call.data["days"])

        for entry in hass.data[DOMAIN].values():
            for entity in entry.get("entities", []):
                if entity._chore_name == chore_name and entity._field == ATTR_DAYS:
                    entity.update_value(days_value)

    async def handle_score_override(call: ServiceCall):
        user_name = call.data["user"]
        new_points = int(call.data["points"])
        score_entry = hass.data.get("scores", {}).get(user_name)
        if score_entry:
            score_entity = next((e for e in score_entry["entities"] if e._field == ATTR_POINTS), None)
            if score_entity:
                score_entity.update_value(new_points)

    hass.services.async_register(DOMAIN, SERVICE_DO_CHORE, handle_do_chore)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_POINTS, handle_update_points)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_DAYS, handle_update_days)
    hass.services.async_register(DOMAIN, SERVICE_SCORE_OVERRIDE, handle_score_override)

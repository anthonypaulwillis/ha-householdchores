from __future__ import annotations
import datetime
import json

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN, CONF_CHORES, CONF_NAME, ATTR_NEXT, ATTR_LAST, ATTR_BY

class ChoreSensor(SensorEntity):
    """A sensor representing a single Chore with extended attributes."""

    _attr_icon = "mdi:check-circle-outline"

    def __init__(self, name: str, initial_data: str | None = None) -> None:
        self._attr_name = f"{name} Chore"
        self._attr_unique_id = f"chore_{name.lower().replace(' ', '_')}"
        self._state = STATE_UNKNOWN

        # Default values
        self._next: datetime.datetime | None = None
        self._last: datetime.datetime | None = None
        self._by: str | None = None
        self._last_overdue: int | None = None
        self._notify: bool = False
        self._points: int | None = None
        self._days: int | None = None
        self._who_notify: list[str] = []

        if initial_data:
            self.load_from_json(initial_data)

    def load_from_json(self, data: str):
        """Load all values from JSON string."""
        try:
            js = json.loads(data)
            self._next = (
                datetime.datetime.strptime(js.get("next"), "%Y-%m-%d %H:%M:%S")
                .replace(tzinfo=datetime.timezone.utc)
                if js.get("next")
                else None
            )
            self._last = (
                datetime.datetime.strptime(js.get("last"), "%Y-%m-%d %H:%M:%S")
                .replace(tzinfo=datetime.timezone.utc)
                if js.get("last")
                else None
            )
            self._by = js.get("by")
            self._last_overdue = js.get("last_overdue")
            self._notify = js.get("notify", False)
            self._points = js.get("points")
            self._days = js.get("days")
            # Ensure who_notify is a list
            who = js.get("who_notify")
            if isinstance(who, str):
                self._who_notify = [who]
            elif isinstance(who, list):
                self._who_notify = who
            else:
                self._who_notify = []
        except Exception as e:
            self._next = None
            self._last = None
            self._by = None
            self._who_notify = []
            self._last_overdue = None
            self._notify = False
            self._points = None
            self._days = None
            # optional: log the error

    @property
    def state(self):
        """Return due/upcoming/unknown."""
        if self._next:
            now = datetime.datetime.now(datetime.timezone.utc)
            if self._next < now:
                return "due"
            return "upcoming"
        return STATE_UNKNOWN

    @property
    def extra_state_attributes(self):
        """Return all chore attributes."""
        return {
            ATTR_NEXT: self._next.isoformat() if self._next else None,
            ATTR_LAST: self._last.isoformat() if self._last else None,
            ATTR_BY: self._by,
            "last_overdue": self._last_overdue,
            "notify": self._notify,
            "points": self._points,
            "days": self._days,
            "who_notify": self._who_notify,
        }

    def mark_done(self, by: str | None = None):
        """Mark chore done."""
        self._last = datetime.datetime.now(datetime.timezone.utc)
        self._by = by if by else self._by
        if self._days:
            self._next = self._last + datetime.timedelta(days=self._days)
        self.async_write_ha_state()

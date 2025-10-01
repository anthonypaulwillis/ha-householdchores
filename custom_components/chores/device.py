from datetime import timedelta
from homeassistant.util.dt import utcnow

class ChoreDevice:
    """Chore device with reactive Status sensor and persistence support."""

    def __init__(self, name: str, points: int = 5, days: int = 7,
                 last_done_date=None, next_due_date=None, last_done_by=""):
        self.name = name
        self.device_id = f"chores_{name.lower().replace(' ', '_')}"

        # Defaults or restored values
        self.points = points
        self.days = days
        self.last_done_by = last_done_by
        self.last_done_date = last_done_date or utcnow()
        self.next_due_date = next_due_date or (utcnow() + timedelta(days=self.days))

        # Status
        self.status = "not due"
        self.status_sensor_entity = None  # Will be set by sensor platform

    def update_status(self):
        """Compute status based on last_done_date and next_due_date."""
        now = utcnow()
        if self.last_done_date and (now - self.last_done_date).total_seconds() < 600:
            self.status = "recent"
        elif self.next_due_date:
            if self.next_due_date < now:
                overdue_days = (now - self.next_due_date).days
                self.status = "overdue" if overdue_days > 2 else "due"
            else:
                self.status = "not due"
        else:
            self.status = "unknown"


class ScoreDevice:
    """Score device for a user, with persistent points."""

    def __init__(self, name: str, points: int = 0):
        self.name = name
        self.points = points

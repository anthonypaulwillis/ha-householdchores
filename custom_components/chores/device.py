from datetime import timedelta
from homeassistant.util.dt import utcnow

class ChoreDevice:
    def __init__(self, name: str):
        self.name = name
        self.device_id = f"chores_{name.lower().replace(' ', '_')}"

        # Default values
        self.points = 5
        self.days = 7
        self.last_done_by = ""

        # Dates: last done = now, next due = 7 days from now
        self.last_done_date = utcnow()
        self.next_due_date = utcnow() + timedelta(days=self.days)

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
    def __init__(self, name: str):
        self.name = name
        self.points = 0

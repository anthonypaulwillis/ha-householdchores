from datetime import timedelta
from homeassistant.util.dt import utcnow


class ChoreDevice:
    def __init__(self, name: str):
        self.name = name
        self.device_id = f"chores_{name.lower().replace(' ', '_')}"
        self.points = 5                # Default points
        self.days = 7                  # Default repeat interval
        self.last_done_by = ""         # Who last completed it (if tracked)

        now = utcnow()
        self.last_done_date = now      # Default to "done now"
        self.next_due_date = now + timedelta(days=self.days)  # Default to 7 days later

        self.last_days_overdue = 0
        self.status = "unknown"

    def update_status(self):
        """Update the chore's status based on due/last done dates."""
        now = utcnow()

        # If just done in the last 10 minutes
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
        self.device_id = f"chores_{name.lower().replace(' ', '_')}"
        self.points = 5  # Default points for Score

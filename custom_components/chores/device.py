from datetime import timedelta
from homeassistant.util.dt import utcnow

class ChoreDevice:
    def __init__(self, name: str, options: dict):
        self.name = name
        self.device_id = f"chores_{name.lower().replace(' ', '_')}"

        now = utcnow()
        self.days = options.get("days", 7)
        self.points = options.get("points", 5)
        self.last_done_by = options.get("last_done_by", "")
        self.last_done_date = options.get("last_done_date", now)
        self.next_due_date = options.get("next_due_date", now + timedelta(days=self.days))
        self.status = "unknown"

    def update_status(self):
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
    def __init__(self, name: str, options: dict):
        self.name = name
        self.device_id = f"score_{name.lower().replace(' ', '_')}"
        self.points = options.get("points", 0)

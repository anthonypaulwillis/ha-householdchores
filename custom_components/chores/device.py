from datetime import timedelta
from homeassistant.util.dt import utcnow

DEVICE_TYPE_CHORE = "chore"
DEVICE_TYPE_SCORE = "score"

class ChoreDevice:
    def __init__(self, name: str):
        self.name = name
        self.device_type = DEVICE_TYPE_CHORE
        self.device_id = f"chores_{name.lower().replace(' ', '_')}"
        self.points = 5
        self.days = 7
        self.last_done_by = ""
        self.last_done_date = utcnow()
        self.next_due_date = utcnow() + timedelta(days=self.days)
        self.status = "unknown"
        self.status_sensor_entity = None

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
    def __init__(self, name: str):
        self.name = name
        self.device_type = DEVICE_TYPE_SCORE
        self.device_id = f"scores_{name.lower().replace(' ', '_')}"
        self.points = 0

from datetime import datetime

class ChoreDevice:
    def __init__(self, name: str):
        self.name = name
        self.points = 0
        self.days = 0
        self.last_done_by = ""
        self.late_done_date: datetime | None = None
        self.next_due_date: datetime | None = None
        self.last_days_overdue = 0
        self.status = "unknown"  # Status updated by sensor or helper

    def update_status(self):
        """Optional helper to recalc status without sensor polling"""
        now = datetime.now()
        if self.late_done_date and (now - self.late_done_date).total_seconds() < 600:
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

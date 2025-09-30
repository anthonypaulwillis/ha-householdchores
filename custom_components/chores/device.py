class ChoreDevice:
    def __init__(self, name: str):
        self.name = name
        self.points = 0
        self.days = 0
        self.last_done_by = ""
        self.late_done_date = None
        self.next_due_date = None
        self.last_days_overdue = 0
        self.status = "unknown"

class ScoreDevice:
    def __init__(self, name: str):
        self.name = name
        self.points = 0

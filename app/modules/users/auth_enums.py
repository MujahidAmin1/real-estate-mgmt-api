import enum

class OnboardingStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"

class UserRole(str, enum.Enum):
    client = "client"
    agent = "agent"
    admin = "admin"

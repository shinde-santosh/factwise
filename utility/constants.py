BASE_URL = '/api/v1/'

MAX_TEAM_USERS = 50
CREATE_DISPLAY_NAME_MAX = 64

"""Status"""
STATUS_OPEN = "OPEN"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_COMPLETE = "COMPLETE"
STATUS_CLOSED = "CLOSED"
TASK_STATUSES = [STATUS_OPEN, STATUS_IN_PROGRESS, STATUS_COMPLETE]

"""Messages"""
MESSAGES = {
    "invalid_json": "Request must be a valid JSON object.",
    "created": " created successfully.",
    "updated": " updated successfully.",
    "not_found": " not found.",
    "already_exists": " already exists.",
    "invalid_status": "Invalid status.",
    "name_cannot_update": "User name cannot be updated.",
    "display_name_max": f"display_name : Ensure this field has no more than {CREATE_DISPLAY_NAME_MAX} characters.",
    "invalid_users": "Users must be a non-empty list of user ids.",
    "max_team_users": f"A team can have max {MAX_TEAM_USERS} users.",
    "board_closed": "Board is already closed.",
    "board_not_open": "Task can be added only to an OPEN board.",
    "tasks_not_complete": "Board can be closed only when all tasks are COMPLETE.",
}

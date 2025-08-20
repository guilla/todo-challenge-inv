import logging

logger = logging.getLogger("todo") 

def log_event(request, action: str, **extra):
    """
    action: 'task_created', 'task_updated', 'task_retrieved', 'task_listed', 'task_deleted', 'task_completed'
    extra:  task_id=..., title=..., status=...
    """
    payload = {
        "action": action,
        "user": getattr(request.user, "username", None),
        "method": request.method,
        "path": request.get_full_path(),
        "request_id": getattr(request, "request_id", "-"),
        **extra,
    }
    logger.info(action, extra=payload)

class TASK_ACTIONS(Enum):
    """
    Enum-like class to define task-related actions for logging.
    'task_created', 'task_updated', 'task_retrieved', 'task_listed', 'task_deleted', 'task_completed'
    """
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_RETRIEVED = "task_retrieved"
    TASK_LISTED = "task_listed"
    TASK_DELETED = "task_deleted"
    TASK_COMPLETED = "task_completed"

"""Mock of pineapple.helpers.notification_helpers — notification levels."""
INFO = 0
WARN = 1
ERROR = 2
OTHER = 3
SUCCESS = 4


def send_notification(message: str, module_name: str, level: int = INFO) -> bool:
    return True

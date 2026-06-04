"""Mock of pineapple.modules — provides Module and Request."""
import json
import logging
from typing import Any, Callable, Dict, List, Optional


class Request:
    def __init__(self):
        self.module: str = ""
        self.action: str = ""

    def __repr__(self):
        return json.dumps(self.__dict__)


class Module:
    """Lightweight stand-in for the SDK Module — no sockets, no /root storage."""

    def __init__(self, name: str, log_level: int = logging.WARNING):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self._action_handlers: Dict[str, Callable[[Request], Any]] = {}
        self._startup_handlers: List[Callable[[], None]] = []
        self._shutdown_handlers: List[Callable[[Optional[int]], None]] = []
        self.notifications: List[dict] = []   # captured for test assertions

    # --- registration ---
    def register_action_handler(self, action: str, handler: Callable[[Request], Any]):
        self._action_handlers[action] = handler

    def handles_action(self, action: str):
        def wrapper(func):
            self.register_action_handler(action, func)
            return func
        return wrapper

    def register_startup_handler(self, handler):
        self._startup_handlers.append(handler)

    def on_start(self):
        def wrapper(func):
            self.register_startup_handler(func)
            return func
        return wrapper

    def register_shutdown_handler(self, handler):
        self._shutdown_handlers.append(handler)

    def on_shutdown(self):
        def wrapper(func):
            self.register_shutdown_handler(func)
            return func
        return wrapper

    def send_notification(self, message: str, level: int) -> bool:
        self.notifications.append({'message': message, 'level': level})
        return True

    # --- test helpers (not part of the real SDK) ---
    def run_startup(self):
        for h in self._startup_handlers:
            h()

    def dispatch(self, action: str, **fields):
        """Build a Request and invoke the registered handler; returns its result."""
        req = Request()
        req.__dict__.update({'module': self.name, 'action': action})
        req.__dict__.update(fields)
        handler = self._action_handlers.get(action)
        if handler is None:
            raise KeyError(f'No handler registered for action {action!r}')
        return handler(req)

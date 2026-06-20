"""Logging system for VISCA Bridge.

Provides thread-safe logging with a custom log() function
that maintains a circular buffer of recent log entries.
"""

from collections import deque
from threading import Lock
from time import time
from visca.config import MAX_LOG_ENTRIES


log_queue = deque(maxlen=MAX_LOG_ENTRIES)
log_lock = Lock()


def log(level: str, msg: str) -> None:
    """Log a message with thread-safety.

    Args:
        level: Log level as string (I, W, E, D for Info, Warning, Error, Debug)
        msg: Log message
    """
    with log_lock:
        entry = {'t': int(time()), 'l': level[0], 'm': msg}
        log_queue.appendleft(entry)
        timestamp = time()
        print(f"[{level}] {msg}")


def get_log_history(limit: int = None) -> list:
    """Get recent log entries from the circular buffer.

    Args:
        limit: Maximum number of entries to return (None = all)

    Returns:
        list: List of log entry dicts with keys: t (timestamp), l (level), m (message)
    """
    with log_lock:
        history = list(log_queue)
        if limit:
            return history[:limit]
        return history

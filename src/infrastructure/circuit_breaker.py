import time
from enum import Enum, auto


class CircuitState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0) -> None:
        self._threshold = failure_threshold
        self._timeout = recovery_timeout
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._last_failure_time = 0.0

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self._timeout:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def record_success(self) -> None:
        self._state = CircuitState.CLOSED
        self._failures = 0

    def record_failure(self) -> None:
        self._failures += 1
        self._last_failure_time = time.monotonic()
        if self._state == CircuitState.HALF_OPEN or self._failures >= self._threshold:
            self._state = CircuitState.OPEN

    def allow_request(self) -> bool:
        state = self.state
        if state == CircuitState.OPEN:
            return False
        if state == CircuitState.HALF_OPEN:
            return True
        return True

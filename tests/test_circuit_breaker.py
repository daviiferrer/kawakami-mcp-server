from unittest.mock import patch

from src.infrastructure.circuit_breaker import CircuitBreaker, CircuitState


class TestCircuitBreakerClosedState:
    def test_initial_state_is_closed(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED

    def test_allows_requests_when_closed(self):
        cb = CircuitBreaker()
        assert cb.allow_request() is True

    def test_stays_closed_after_success(self):
        cb = CircuitBreaker()
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_stays_closed_below_threshold(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        assert cb.allow_request() is True


class TestCircuitBreakerOpenState:
    def test_opens_after_reaching_failure_threshold(self):
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_blocks_requests_when_open(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        assert cb.allow_request() is False

    def test_failure_count_resets_after_success(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED


class TestCircuitBreakerHalfOpenState:
    def test_transitions_to_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=10.0)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        target = "src.infrastructure.circuit_breaker.time.monotonic"
        with patch(target, return_value=cb._last_failure_time + 10.0):
            assert cb.state == CircuitState.HALF_OPEN

    def test_allows_request_in_half_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=10.0)
        cb.record_failure()

        target = "src.infrastructure.circuit_breaker.time.monotonic"
        with patch(target, return_value=cb._last_failure_time + 10.0):
            assert cb.allow_request() is True

    def test_closes_on_success_from_half_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=10.0)
        cb.record_failure()

        target = "src.infrastructure.circuit_breaker.time.monotonic"
        with patch(target, return_value=cb._last_failure_time + 10.0):
            _ = cb.state  # trigger transition to HALF_OPEN

        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb._failures == 0

    def test_reopens_on_failure_from_half_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=10.0)
        cb.record_failure()

        target = "src.infrastructure.circuit_breaker.time.monotonic"
        with patch(target, return_value=cb._last_failure_time + 10.0):
            _ = cb.state  # trigger transition to HALF_OPEN

        cb.record_failure()
        assert cb.state == CircuitState.OPEN

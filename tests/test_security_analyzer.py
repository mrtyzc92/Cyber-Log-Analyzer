from datetime import datetime

from cyber_log_analyzer.analyzers.security_analyzer import (
    find_suspicious_login_attempts,
)
from cyber_log_analyzer.models.log_entry import LogEntry


def make_log_entry(
    ip_address: str,
    event: str,
) -> LogEntry:
    return LogEntry(
        timestamp=datetime(2026, 8, 18, 9, 10, 15),
        level="WARNING",
        ip_address=ip_address,
        event=event,
        username="test-user",
    )


def test_returns_ip_at_threshold():
    entries = [
        make_log_entry("192.168.1.25", "LOGIN_FAILED"),
        make_log_entry("192.168.1.25", "LOGIN_FAILED"),
        make_log_entry("192.168.1.25", "LOGIN_FAILED"),
    ]

    result = find_suspicious_login_attempts(
        entries,
        threshold=3,
    )

    assert result == {
        "192.168.1.25": 3,
    }


def test_excludes_ip_below_threshold():
    entries = [
        make_log_entry("192.168.1.25", "LOGIN_FAILED"),
        make_log_entry("192.168.1.25", "LOGIN_FAILED"),
    ]

    result = find_suspicious_login_attempts(
        entries,
        threshold=3,
    )

    assert result == {}


def test_ignores_events_other_than_failed_login():
    entries = [
        make_log_entry("192.168.1.25", "LOGIN_SUCCESS"),
        make_log_entry("192.168.1.25", "LOGOUT"),
        make_log_entry("192.168.1.25", "ACCESS_DENIED"),
    ]

    result = find_suspicious_login_attempts(
        entries,
        threshold=1,
    )

    assert result == {}
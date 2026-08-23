from collections import Counter
from cyber_log_analyzer.models.log_entry import LogEntry

def find_suspicious_login_attempts(
        entries: list[LogEntry],
        threshold: int = 3
) ->  dict[str, int]:
    """Return IP addresses with failed login counts at or above the threshold."""

    failed_attempts = Counter(
        entry.ip_address
        for entry in entries
        if entry.event == "LOGIN_FAILED"
    )

    return {
        ip_address: count
        for ip_address, count in failed_attempts.items()
        if count >= threshold
    }
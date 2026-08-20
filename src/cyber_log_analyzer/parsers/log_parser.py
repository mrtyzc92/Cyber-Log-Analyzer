from datetime import datetime

from cyber_log_analyzer.models.log_entry import LogEntry


def parse_log_line(line: str) -> LogEntry:
    """Convert one raw log line into a LogEntry object."""

    parts = [part.strip() for part in line.split("|")]

    if len(parts) != 5:
        raise ValueError(
            f"Invalid log line: expected 5 fields, got {len(parts)}"
        )

    timestamp_text, level, ip_address, event, username = parts

    timestamp = datetime.strptime(
        timestamp_text,
        "%Y-%m-%d %H:%M:%S",
    )

    return LogEntry(
        timestamp=timestamp,
        level=level,
        ip_address=ip_address,
        event=event,
        username=username,
    )

def parse_log_lines(lines: list[str]) -> list[LogEntry]:
    """Convert multiple raw log lines into LogEntry objects."""

    return [parse_log_line(line) for line in lines]
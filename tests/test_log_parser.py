from datetime import datetime

import pytest

from cyber_log_analyzer.models.log_entry import LogEntry
from cyber_log_analyzer.parsers.log_parser import (
    parse_log_line,
    parse_log_lines,
)


def test_parse_log_line_returns_log_entry():
    line = (
        "2026-08-18 09:10:15 | INFO | "
        "192.168.1.10 | LOGIN_SUCCESS | mert"
    )

    result = parse_log_line(line)

    assert result == LogEntry(
        timestamp=datetime(2026, 8, 18, 9, 10, 15),
        level="INFO",
        ip_address="192.168.1.10",
        event="LOGIN_SUCCESS",
        username="mert",
    )


def test_parse_log_line_rejects_wrong_field_count():
    invalid_line = "2026-08-18 09:10:15 | INFO"

    with pytest.raises(
        ValueError,
        match="expected 5 fields",
    ):
        parse_log_line(invalid_line)


def test_parse_log_line_rejects_invalid_timestamp():
    invalid_line = (
        "18-08-2026 09:10:15 | INFO | "
        "192.168.1.10 | LOGIN_SUCCESS | mert"
    )

    with pytest.raises(ValueError):
        parse_log_line(invalid_line)


def test_parse_log_lines_parses_multiple_lines():
    lines = [
        (
            "2026-08-18 09:10:15 | INFO | "
            "192.168.1.10 | LOGIN_SUCCESS | mert"
        ),
        (
            "2026-08-18 09:12:42 | WARNING | "
            "192.168.1.25 | LOGIN_FAILED | admin"
        ),
    ]

    result = parse_log_lines(lines)

    assert len(result) == 2
    assert result[0].event == "LOGIN_SUCCESS"
    assert result[1].event == "LOGIN_FAILED"
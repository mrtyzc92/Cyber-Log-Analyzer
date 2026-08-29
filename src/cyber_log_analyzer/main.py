from pathlib import Path

from cyber_log_analyzer.analyzers.security_analyzer import (
    find_suspicious_login_attempts,
)
from cyber_log_analyzer.parsers.log_parser import parse_log_lines
from cyber_log_analyzer.readers.file_reader import read_log_lines
from cyber_log_analyzer.reporters.text_reporter import (
    format_security_report,
)


def analyze_log_file(
    file_path: str | Path,
    threshold: int = 3,
) -> str:
    """Analyze a log file and return a readable security report."""

    lines = read_log_lines(file_path)
    entries = parse_log_lines(lines)

    suspicious_attempts = find_suspicious_login_attempts(
        entries,
        threshold=threshold,
    )

    return format_security_report(suspicious_attempts)


def main() -> None:
    """Run the application with the sample log file."""

    report = analyze_log_file(
        "data/raw/sample.log",
        threshold=3,
    )

    print(report)


if __name__ == "__main__":
    main()
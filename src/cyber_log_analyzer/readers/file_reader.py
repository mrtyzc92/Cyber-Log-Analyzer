from pathlib import Path


def read_log_lines(file_path: str | Path) -> list[str]:
    """Read non-empty lines from a UTF-8 encoded log file."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Log file not found: {path}")

    with path.open(mode="r", encoding="utf-8") as log_file:
        return [line.strip() for line in log_file if line.strip()]
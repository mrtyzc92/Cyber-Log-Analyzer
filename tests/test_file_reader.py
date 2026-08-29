import pytest

from cyber_log_analyzer.readers.file_reader import read_log_lines


def test_read_log_lines_returns_non_empty_lines(tmp_path):
    log_file = tmp_path / "sample.log"

    log_file.write_text(
        "first line\n\n second line \n",
        encoding="utf-8",
    )

    result = read_log_lines(log_file)

    assert result == [
        "first line",
        "second line",
    ]


def test_read_log_lines_raises_error_when_file_is_missing(tmp_path):
    missing_file = tmp_path / "missing.log"

    with pytest.raises(
        FileNotFoundError,
        match="Log file not found",
    ):
        read_log_lines(missing_file)
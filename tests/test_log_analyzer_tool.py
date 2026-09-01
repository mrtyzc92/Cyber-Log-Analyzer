from cyber_log_analyzer.agents.log_analyzer_tool import LogAnalyzerTool


def test_log_analyzer_tool_analyzes_log_file(tmp_path):
    log_file = tmp_path / "security.log"
    log_file.write_text(
        "\n".join(
            [
                "2026-08-18 09:12:42 | WARNING | "
                "192.168.1.25 | LOGIN_FAILED | admin",
                "2026-08-18 09:13:01 | WARNING | "
                "192.168.1.25 | LOGIN_FAILED | admin",
                "2026-08-18 09:13:19 | WARNING | "
                "192.168.1.25 | LOGIN_FAILED | admin",
            ]
        ),
        encoding="utf-8",
    )

    tool = LogAnalyzerTool(threshold=3)
    result = tool.run(str(log_file))

    assert tool.name == "log_analyzer"
    assert result.tool_name == "log_analyzer"
    assert result.success is True
    assert "192.168.1.25" in result.observation
    assert result.error is None

def test_log_analyzer_tool_returns_failure_when_file_is_missing(tmp_path):
    missing_log_file = tmp_path / "missing.log"
    tool = LogAnalyzerTool(threshold=3)

    result = tool.run(str(missing_log_file))

    assert result.tool_name == "log_analyzer"
    assert result.success is False
    assert result.observation == "Log analysis failed"
    assert result.error is not None

def test_log_analyzer_tool_returns_failure_for_malformed_log(tmp_path):
    malformed_log_file = tmp_path / "malformed.log"
    malformed_log_file.write_text(
        "this is not a valid log line",
        encoding="utf-8",
    )
    tool = LogAnalyzerTool(threshold=3)

    result = tool.run(str(malformed_log_file))

    assert result.tool_name == "log_analyzer"
    assert result.success is False
    assert result.observation == "Log analysis failed"
    assert result.error is not None
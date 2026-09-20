from cyber_log_analyzer.agents.tools import AgentTool, ToolResult
from cyber_log_analyzer.main import analyze_log_file


class LogAnalyzerTool(AgentTool):
    """Expose the existing log analysis pipeline as an agent tool."""

    name = "log_analyzer"

    def __init__(self, threshold: int = 3) -> None:
        self.threshold = threshold

    def run(self, tool_input: str) -> ToolResult:
        try:
            report = analyze_log_file(
                tool_input,
                threshold=self.threshold,
            )
        except (
            FileNotFoundError,
            UnicodeDecodeError,
            ValueError,
        ) as error:
            return ToolResult(
                tool_name=self.name,
                success=False,
                observation="Log analysis failed",
                error=str(error),
            )

        return ToolResult(
            tool_name=self.name,
            success=True,
            observation=report,
        )

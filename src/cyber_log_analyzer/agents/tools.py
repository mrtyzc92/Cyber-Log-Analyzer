from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolResult:
    """Represent the observation returned by an agent tool."""

    tool_name: str
    success: bool
    observation: str
    error: str | None = None


class AgentTool(ABC):
    """Define the contract implemented by every agent tool."""

    name: str

    @abstractmethod
    def run(self, tool_input: str) -> ToolResult:
        """Execute the tool and return a structured result."""
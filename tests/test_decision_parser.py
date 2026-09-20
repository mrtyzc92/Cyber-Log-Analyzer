import pytest

from cyber_log_analyzer.agents.decision_parser import (
    DecisionParseError,
    parse_agent_decision,
)
from cyber_log_analyzer.agents.decisions import AgentAction


def test_parse_agent_decision_converts_valid_json():
    raw_output = """
    {
        "action": "use_tool",
        "reason": "The security log must be analyzed",
        "tool_name": "log_analyzer",
        "tool_input": "security.log"
    }
    """

    decision = parse_agent_decision(raw_output)

    assert decision.action is AgentAction.USE_TOOL
    assert decision.reason == "The security log must be analyzed"
    assert decision.tool_name == "log_analyzer"
    assert decision.tool_input == "security.log"


def test_parse_agent_decision_rejects_invalid_json():
    with pytest.raises(
        DecisionParseError,
        match="Model output must be valid JSON",
    ):
        parse_agent_decision("not-json")


def test_parse_agent_decision_rejects_unknown_action():
    raw_output = """
    {
        "action": "delete_everything",
        "reason": "The model requested an unsupported action"
    }
    """

    with pytest.raises(
        DecisionParseError,
        match="Unsupported agent action: delete_everything",
    ):
        parse_agent_decision(raw_output)


def test_parse_agent_decision_rejects_empty_reason():
    raw_output = '{"action": "complete", "reason": "   "}'

    with pytest.raises(
        DecisionParseError,
        match="Decision reason must be a non-empty string",
    ):
        parse_agent_decision(raw_output)


def test_parse_agent_decision_requires_tool_fields_for_tool_action():
    raw_output = """
    {
        "action": "use_tool",
        "reason": "The log must be analyzed"
    }
    """

    with pytest.raises(
        DecisionParseError,
        match="USE_TOOL decision requires a non-empty tool_name",
    ):
        parse_agent_decision(raw_output)


def test_parse_agent_decision_rejects_tool_fields_for_final_action():
    raw_output = """
    {
        "action": "complete",
        "reason": "The task is complete",
        "tool_name": "log_analyzer"
    }
    """

    with pytest.raises(
        DecisionParseError,
        match="COMPLETE decision must not include tool fields",
    ):
        parse_agent_decision(raw_output)


def test_parse_agent_decision_rejects_non_object_json():
    with pytest.raises(
        DecisionParseError,
        match="Model output must be a JSON object",
    ):
        parse_agent_decision('["complete", "finished"]')


def test_parse_agent_decision_rejects_unexpected_fields():
    raw_output = """
    {
        "action": "complete",
        "reason": "The task is complete",
        "command": "format-disk"
    }
    """

    with pytest.raises(
        DecisionParseError,
        match="Unexpected decision fields: command",
    ):
        parse_agent_decision(raw_output)


def test_parse_agent_decision_requires_string_tool_input():
    raw_output = """
    {
        "action": "use_tool",
        "reason": "The log must be analyzed",
        "tool_name": "log_analyzer"
    }
    """

    with pytest.raises(
        DecisionParseError,
        match="USE_TOOL decision requires a string tool_input",
    ):
        parse_agent_decision(raw_output)

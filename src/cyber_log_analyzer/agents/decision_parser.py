import json

from cyber_log_analyzer.agents.decisions import AgentAction, AgentDecision


DECISION_FIELDS = {
    "action",
    "reason",
    "tool_name",
    "tool_input",
}


class DecisionParseError(ValueError):
    """Report a model response that violates the decision contract."""


def parse_agent_decision(raw_output: str) -> AgentDecision:
    """Validate a JSON model response and create an agent decision."""

    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError as error:
        raise DecisionParseError(
            "Model output must be valid JSON"
        ) from error

    if not isinstance(payload, dict):
        raise DecisionParseError("Model output must be a JSON object")

    unexpected_fields = sorted(set(payload) - DECISION_FIELDS)
    if unexpected_fields:
        raise DecisionParseError(
            "Unexpected decision fields: "
            + ", ".join(unexpected_fields)
        )

    action_value = payload.get("action")
    if not isinstance(action_value, str) or not action_value.strip():
        raise DecisionParseError(
            "Decision action must be a non-empty string"
        )

    try:
        action = AgentAction(action_value)
    except ValueError as error:
        raise DecisionParseError(
            f"Unsupported agent action: {action_value}"
        ) from error

    reason = payload.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        raise DecisionParseError(
            "Decision reason must be a non-empty string"
        )

    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input")

    if action is AgentAction.USE_TOOL:
        if not isinstance(tool_name, str) or not tool_name.strip():
            raise DecisionParseError(
                "USE_TOOL decision requires a non-empty tool_name"
            )
        if not isinstance(tool_input, str):
            raise DecisionParseError(
                "USE_TOOL decision requires a string tool_input"
            )
    elif tool_name is not None or tool_input is not None:
        raise DecisionParseError(
            f"{action.name} decision must not include tool fields"
        )

    return AgentDecision(
        action=action,
        reason=reason,
        tool_name=tool_name,
        tool_input=tool_input,
    )

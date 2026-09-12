from cyber_log_analyzer.agents.decisions import AgentAction, AgentDecision


def test_agent_action_defines_available_actions():
    assert AgentAction.USE_TOOL == "use_tool"
    assert AgentAction.COMPLETE == "complete"
    assert AgentAction.FAIL == "fail"

def test_agent_decision_represents_tool_selection():
    decision = AgentDecision(
        action=AgentAction.USE_TOOL,
        reason="The security log must be analyzed",
        tool_name="log_analyzer",
        tool_input="security.log",
    )

    assert decision.action is AgentAction.USE_TOOL
    assert decision.reason == "The security log must be analyzed"
    assert decision.tool_name == "log_analyzer"
    assert decision.tool_input == "security.log"
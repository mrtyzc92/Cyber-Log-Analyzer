from cyber_log_analyzer.agents.decisions import AgentAction
from cyber_log_analyzer.agents.llm_decision_maker import LLMDecisionMaker
from cyber_log_analyzer.agents.memory import AgentMemory
from cyber_log_analyzer.agents.state import AgentState


class FakeLanguageModel:
    def __init__(self, response: str) -> None:
        self.response = response
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response


def test_llm_decision_maker_returns_validated_tool_decision():
    model = FakeLanguageModel(
        """
        {
            "action": "use_tool",
            "reason": "The log must be analyzed",
            "tool_name": "log_analyzer",
            "tool_input": "sample.log"
        }
        """
    )
    decision_maker = LLMDecisionMaker(
        model=model,
        available_tools=("log_analyzer",),
    )
    state = AgentState(goal="Analyze the uploaded log")

    decision = decision_maker.decide(state)

    assert decision.action is AgentAction.USE_TOOL
    assert decision.tool_name == "log_analyzer"
    assert decision.tool_input == "sample.log"
    assert "Analyze the uploaded log" in model.prompts[0]
    assert '"log_analyzer"' in model.prompts[0]


def test_llm_decision_maker_includes_observations_in_prompt():
    model = FakeLanguageModel(
        '{"action": "complete", "reason": "Analysis finished"}'
    )
    decision_maker = LLMDecisionMaker(
        model=model,
        available_tools=("log_analyzer",),
    )
    state = AgentState(goal="Analyze the uploaded log")
    state.record_observation("Suspicious IP found")

    decision_maker.decide(state)

    assert "Suspicious IP found" in model.prompts[0]


def test_llm_decision_maker_fails_closed_for_unavailable_tool():
    model = FakeLanguageModel(
        """
        {
            "action": "use_tool",
            "reason": "Use an unapproved capability",
            "tool_name": "delete_files",
            "tool_input": "all"
        }
        """
    )
    decision_maker = LLMDecisionMaker(
        model=model,
        available_tools=("log_analyzer",),
    )

    decision = decision_maker.decide(AgentState(goal="Analyze a log"))

    assert decision.action is AgentAction.FAIL
    assert decision.reason == "Model selected unavailable tool: delete_files"


def test_llm_decision_maker_fails_closed_for_invalid_output():
    model = FakeLanguageModel("not-json")
    decision_maker = LLMDecisionMaker(
        model=model,
        available_tools=("log_analyzer",),
    )

    decision = decision_maker.decide(AgentState(goal="Analyze a log"))

    assert decision.action is AgentAction.FAIL
    assert decision.reason == (
        "Invalid model decision: Model output must be valid JSON"
    )


class FailingLanguageModel:
    def generate(self, prompt: str) -> str:
        raise RuntimeError("model service unavailable")


def test_llm_decision_maker_exposes_model_failure_as_fail_decision():
    decision_maker = LLMDecisionMaker(
        model=FailingLanguageModel(),
        available_tools=("log_analyzer",),
    )

    decision = decision_maker.decide(AgentState(goal="Analyze a log"))

    assert decision.action is AgentAction.FAIL
    assert decision.reason == "Decision model failed: model service unavailable"


def test_llm_decision_maker_includes_recent_memory_in_prompt():
    memory = AgentMemory()
    previous_state = AgentState(goal="Analyze yesterday's log")
    previous_state.complete("No suspicious activity")
    memory.remember(previous_state)
    model = FakeLanguageModel(
        '{"action": "complete", "reason": "Analysis finished"}'
    )
    decision_maker = LLMDecisionMaker(
        model=model,
        available_tools=("log_analyzer",),
        memory=memory,
    )

    decision_maker.decide(AgentState(goal="Analyze today's log"))

    assert "Analyze yesterday's log" in model.prompts[0]
    assert "No suspicious activity" in model.prompts[0]

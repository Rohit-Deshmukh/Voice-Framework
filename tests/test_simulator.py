import pytest

from models.test_cases import TestCase, TurnExpectation
from services.simulator import SimulatorAgent


@pytest.mark.asyncio
async def test_simulator_respects_script_without_disfluencies() -> None:
    test_case = TestCase(
        test_id="sim_basic",
        persona="Direct",
        turns=[
            TurnExpectation(
                step_order=1,
                user_input="Hi agent",
                expected_agent_response_keywords=["hello"],
                exact_match_required=False,
            )
        ],
    )

    simulator = SimulatorAgent(naturalize_user_prompts=False, disfluency_rate=0.0)
    transcript = await simulator.run(test_case)

    assert len(transcript) == 2
    assert transcript[0]["text"] == "Hi agent"
    assert transcript[0]["speaker"] == "user"


def test_simulator_injects_disfluency(monkeypatch: pytest.MonkeyPatch) -> None:
    simulator = SimulatorAgent(disfluency_rate=1.0)

    monkeypatch.setattr("services.simulator.random.random", lambda: 0.0)
    monkeypatch.setattr("services.simulator.random.choice", lambda seq: seq[0])
    monkeypatch.setattr("services.simulator.random.randint", lambda _a, _b: 0)

    output = simulator._inject_disfluencies("I need assistance")
    assert output.startswith("um ")

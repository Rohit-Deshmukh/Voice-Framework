from models.test_cases import TestCase, TurnExpectation
from services.validation import validate_turn_by_turn


def _build_test_case() -> TestCase:
    return TestCase(
        test_id="case",
        persona="Tester",
        turns=[
            TurnExpectation(
                step_order=1,
                user_input="Hello",
                expected_agent_response_keywords=["hi", "there"],
                exact_match_required=False,
            ),
            TurnExpectation(
                step_order=2,
                user_input="Need help",
                expected_agent_response_keywords=["help", "options"],
                exact_match_required=False,
            ),
        ],
    )


def test_validate_turn_by_turn_generates_metrics() -> None:
    test_case = _build_test_case()
    transcript = [
        {"speaker": "user", "text": "Hello", "step_order": 1},
        {"speaker": "agent", "text": "Hi there, welcome!", "step_order": 1},
        {"speaker": "user", "text": "Need help", "step_order": 2},
        {"speaker": "agent", "text": "Sure, let me check", "step_order": 2},
    ]

    report = validate_turn_by_turn(transcript, test_case)

    assert report["overall_passed"] is False
    metrics = report["metrics"]
    assert metrics["total_steps"] == 2
    assert metrics["steps_passed"] == 1
    assert metrics["failure_steps"] == [2]
    assert metrics["first_failure_step"] == 2
    assert metrics["user_deviation_detected"] is False
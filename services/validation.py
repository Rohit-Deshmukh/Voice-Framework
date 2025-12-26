"""Turn-by-turn validation utilities for deterministic transcripts."""
from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from models.test_cases import TestCase, TurnExpectation


TranscriptRow = Dict[str, Any]


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _contains_keywords(text: str, keywords: List[str]) -> bool:
    normalized = _normalize(text)
    return all(keyword.lower() in normalized for keyword in keywords)


def _find_next_speaker(
    transcript: Sequence[TranscriptRow],
    start_index: int,
    speaker: str,
) -> Tuple[int, TranscriptRow]:
    for idx in range(start_index + 1, len(transcript)):
        row = transcript[idx]
        if row.get("speaker") == speaker:
            return idx, row
    raise ValueError(f"Transcript missing speaker '{speaker}' after index {start_index}")


def validate_turn_by_turn(
    transcript: Sequence[TranscriptRow],
    test_case: TestCase,
) -> Dict[str, Any]:
    """Map transcript turns to expectations and surface granular failures."""

    report_steps: List[Dict[str, Any]] = []
    failures: List[str] = []
    cursor = -1

    for expectation in test_case.turns:
        try:
            user_idx, user_row = _find_next_speaker(transcript, cursor, speaker="user")
        except ValueError as err:
            failure = f"Step {expectation.step_order} Failed: Missing user input in transcript"
            failures.append(failure)
            report_steps.append(
                {
                    "step_order": expectation.step_order,
                    "expected_user_input": expectation.user_input,
                    "actual_user_input": None,
                    "agent_response": None,
                    "passed": False,
                    "details": str(err),
                }
            )
            break

        cursor = user_idx
        actual_user_text = user_row.get("text", "")
        user_match = expectation.user_input.lower() in _normalize(actual_user_text)

        try:
            agent_idx, agent_row = _find_next_speaker(transcript, cursor, speaker="agent")
        except ValueError as err:
            failure = f"Step {expectation.step_order} Failed: Agent never responded"
            failures.append(failure)
            report_steps.append(
                {
                    "step_order": expectation.step_order,
                    "expected_user_input": expectation.user_input,
                    "actual_user_input": actual_user_text,
                    "agent_response": None,
                    "passed": False,
                    "details": str(err),
                }
            )
            break

        cursor = agent_idx
        agent_text = agent_row.get("text", "")
        if expectation.exact_match_required:
            expected_phrase = " ".join(expectation.expected_agent_response_keywords)
            agent_pass = _normalize(agent_text) == _normalize(expected_phrase)
        else:
            agent_pass = _contains_keywords(agent_text, expectation.expected_agent_response_keywords)

        step_pass = agent_pass and user_match
        if not step_pass:
            failure_reason = []
            if not user_match:
                failure_reason.append("User deviation detected")
            if not agent_pass:
                failure_reason.append(
                    "Missing keywords" if not expectation.exact_match_required else "Exact match failed"
                )
            failure_message = (
                f"Step {expectation.step_order} Failed: Expected {expectation.expected_agent_response_keywords}, "
                f"got '{agent_text or 'NO_RESPONSE'}'"
            )
            failures.append(failure_message)
        else:
            failure_reason = []

        report_steps.append(
            {
                "step_order": expectation.step_order,
                "expected_user_input": expectation.user_input,
                "actual_user_input": actual_user_text,
                "expected_keywords": expectation.expected_agent_response_keywords,
                "exact_match_required": expectation.exact_match_required,
                "agent_response": agent_text,
                "passed": step_pass,
                "details": "; ".join(failure_reason) if failure_reason else None,
            }
        )

    total_steps = len(report_steps)
    steps_passed = sum(1 for step in report_steps if step.get("passed"))
    failure_steps = [step["step_order"] for step in report_steps if not step.get("passed")]
    user_deviation_detected = any(
        step.get("details") and "User deviation" in step["details"] for step in report_steps
    )

    return {
        "overall_passed": not failures and all(step["passed"] for step in report_steps),
        "failures": failures,
        "steps": report_steps,
        "metrics": {
            "total_steps": total_steps,
            "steps_passed": steps_passed,
            "steps_failed": max(total_steps - steps_passed, 0),
            "failure_steps": failure_steps,
            "first_failure_step": failure_steps[0] if failure_steps else None,
            "user_deviation_detected": user_deviation_detected,
            "coverage": (steps_passed / total_steps) if total_steps else 0.0,
        },
    }

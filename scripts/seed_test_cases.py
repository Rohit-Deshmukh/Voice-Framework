"""Seed deterministic test cases into the database for local dev."""
from __future__ import annotations

import asyncio
from typing import List

from core.database import init_db, session_scope
from models.db_models import TestCaseRecord
from models.test_cases import TestCase, TurnExpectation


SAMPLE_TEST_CASES: List[TestCase] = [
    TestCase(
        test_id="billing_inquiry_v1",
        persona="Calm Customer",
        turns=[
            TurnExpectation(
                step_order=1,
                user_input="Hi, I noticed my bill jumped this month.",
                expected_agent_response_keywords=["account", "review", "details"],
                exact_match_required=False,
            ),
            TurnExpectation(
                step_order=2,
                user_input="Can you explain the extra charges?",
                expected_agent_response_keywords=["overage", "usage", "explain"],
                exact_match_required=False,
            ),
            TurnExpectation(
                step_order=3,
                user_input="Thanks, what are my options to lower it?",
                expected_agent_response_keywords=["discount", "plan", "offer"],
                exact_match_required=False,
            ),
        ],
    ),
    TestCase(
        test_id="appointment_booking_v1",
        persona="Impatient Caller",
        turns=[
            TurnExpectation(
                step_order=1,
                user_input="I need to schedule a service visit.",
                expected_agent_response_keywords=["availability", "date"],
                exact_match_required=False,
            ),
            TurnExpectation(
                step_order=2,
                user_input="Morning slots only, please.",
                expected_agent_response_keywords=["morning", "confirm"],
                exact_match_required=False,
            ),
            TurnExpectation(
                step_order=3,
                user_input="Send me a confirmation text.",
                expected_agent_response_keywords=["text", "confirmation"],
                exact_match_required=False,
            ),
        ],
    ),
]


async def upsert_test_case(test_case: TestCase) -> None:
    async with session_scope() as session:
        existing = await session.get(TestCaseRecord, test_case.test_id)
        if existing:
            existing.persona = test_case.persona
            existing.turns = [turn.dict() for turn in test_case.turns]
        else:
            session.add(TestCaseRecord.from_domain(test_case))


async def main() -> None:
    await init_db()
    for case in SAMPLE_TEST_CASES:
        await upsert_test_case(case)
    print(f"Seeded {len(SAMPLE_TEST_CASES)} test cases.")


if __name__ == "__main__":
    asyncio.run(main())

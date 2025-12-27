"""Seed deterministic test cases into storage for local dev."""
from __future__ import annotations

import asyncio
from typing import List

from core.config import get_settings
from core.storage import get_in_memory_test_case_store
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


async def upsert_test_case_db(test_case: TestCase) -> None:
    """Upsert test case to database (legacy method)."""
    from core.database import session_scope
    from models.db_models import TestCaseRecord
    
    async with session_scope() as session:
        existing = await session.get(TestCaseRecord, test_case.test_id)
        if existing:
            existing.persona = test_case.persona
            existing.turns = [turn.dict() for turn in test_case.turns]
        else:
            session.add(TestCaseRecord.from_domain(test_case))


async def main() -> None:
    settings = get_settings()
    
    if settings.use_database:
        # Use database storage
        from core.database import init_db
        await init_db()
        for case in SAMPLE_TEST_CASES:
            await upsert_test_case_db(case)
        print(f"Seeded {len(SAMPLE_TEST_CASES)} test cases to database.")
    else:
        # Use in-memory storage
        store = get_in_memory_test_case_store()
        for case in SAMPLE_TEST_CASES:
            await store.upsert(case)
        print(f"Seeded {len(SAMPLE_TEST_CASES)} test cases to in-memory storage.")
        print("Note: In-memory storage is ephemeral. Test cases will be lost when the application restarts.")
        print("The test cases will be automatically loaded when the API starts.")


if __name__ == "__main__":
    asyncio.run(main())

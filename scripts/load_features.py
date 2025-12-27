"""Load test cases from feature files into storage."""
from __future__ import annotations

import asyncio
from pathlib import Path

from core.config import get_settings
from core.feature_parser import load_all_features
from core.storage import get_in_memory_test_case_store
from models.test_cases import TestCase


async def upsert_test_case_db(test_case: TestCase) -> None:
    """Insert or update a test case in the database."""
    from core.database import session_scope
    from models.db_models import TestCaseRecord
    
    async with session_scope() as session:
        existing = await session.get(TestCaseRecord, test_case.test_id)
        if existing:
            print(f"  Updating existing test case: {test_case.test_id}")
            existing.persona = test_case.persona
            existing.turns = [turn.model_dump() for turn in test_case.turns]
        else:
            print(f"  Adding new test case: {test_case.test_id}")
            session.add(TestCaseRecord.from_domain(test_case))


async def main() -> None:
    """Load all feature files and insert test cases into storage."""
    settings = get_settings()
    
    # Load test cases from feature files
    features_dir = Path(__file__).parent.parent / "features"
    
    if not features_dir.exists():
        print(f"Error: Features directory not found at {features_dir}")
        return
    
    print(f"Loading test cases from feature files in: {features_dir}")
    test_cases = load_all_features(features_dir)
    
    if not test_cases:
        print("No test cases found in feature files.")
        return
    
    print(f"\nFound {len(test_cases)} test case(s) in feature files:")
    for case in test_cases:
        print(f"  - {case.test_id}: {case.persona} ({len(case.turns)} turns)")
    
    if settings.use_database:
        # Use database storage
        from core.database import init_db
        await init_db()
        print("\nLoading test cases into database...")
        for case in test_cases:
            await upsert_test_case_db(case)
        print(f"\n✓ Successfully loaded {len(test_cases)} test case(s) from feature files to database.")
    else:
        # Use in-memory storage
        print("\nLoading test cases into in-memory storage...")
        store = get_in_memory_test_case_store()
        for case in test_cases:
            print(f"  Loading: {case.test_id}")
            await store.upsert(case)
        print(f"\n✓ Successfully loaded {len(test_cases)} test case(s) from feature files to in-memory storage.")
        print("Note: In-memory storage is ephemeral. Test cases will be lost when the application restarts.")


if __name__ == "__main__":
    asyncio.run(main())

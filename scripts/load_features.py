"""Load test cases from feature files into the database."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import List

from core.database import init_db, session_scope
from core.feature_parser import load_all_features
from models.db_models import TestCaseRecord
from models.test_cases import TestCase


async def upsert_test_case(test_case: TestCase) -> None:
    """Insert or update a test case in the database."""
    async with session_scope() as session:
        existing = await session.get(TestCaseRecord, test_case.test_id)
        if existing:
            print(f"  Updating existing test case: {test_case.test_id}")
            existing.persona = test_case.persona
            existing.turns = [turn.dict() for turn in test_case.turns]
        else:
            print(f"  Adding new test case: {test_case.test_id}")
            session.add(TestCaseRecord.from_domain(test_case))


async def main() -> None:
    """Load all feature files and insert test cases into the database."""
    await init_db()
    
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
    
    print("\nLoading test cases into database...")
    for case in test_cases:
        await upsert_test_case(case)
    
    print(f"\n✓ Successfully loaded {len(test_cases)} test case(s) from feature files.")


if __name__ == "__main__":
    asyncio.run(main())

"""Database-backed storage implementation (optional)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlmodel import select

from core.database import session_scope
from core.storage import TestCaseStore, TestRunStore
from models.db_models import TestCaseRecord, TestRun
from models.test_cases import TestCase


class DatabaseTestCaseStore(TestCaseStore):
    """Database-backed implementation of test case storage."""
    
    async def get(self, test_id: str) -> Optional[TestCase]:
        async with session_scope() as session:
            record = await session.get(TestCaseRecord, test_id)
            return record.to_domain() if record else None
    
    async def list_all(self) -> List[TestCase]:
        async with session_scope() as session:
            result = await session.exec(select(TestCaseRecord).order_by(TestCaseRecord.test_id))
            records = result.all()
            return [record.to_domain() for record in records]
    
    async def upsert(self, test_case: TestCase) -> None:
        async with session_scope() as session:
            existing = await session.get(TestCaseRecord, test_case.test_id)
            if existing:
                existing.persona = test_case.persona
                existing.turns = [turn.model_dump() for turn in test_case.turns]
            else:
                session.add(TestCaseRecord.from_domain(test_case))
    
    async def delete(self, test_id: str) -> bool:
        async with session_scope() as session:
            record = await session.get(TestCaseRecord, test_id)
            if record:
                await session.delete(record)
                return True
            return False


class DatabaseTestRunStore(TestRunStore):
    """Database-backed implementation of test run storage."""
    
    async def create(
        self,
        test_id: str,
        provider: str,
        mode: str,
        provider_call_id: Optional[str] = None,
    ) -> str:
        async with session_scope() as session:
            test_run = TestRun(
                test_id=test_id,
                provider=provider,
                mode=mode,
                status="initiated" if mode == "live" else "completed",
                provider_call_id=provider_call_id,
            )
            session.add(test_run)
            await session.flush()  # Get the ID
            return test_run.id
    
    async def get(self, run_id: str) -> Optional[Dict[str, Any]]:
        async with session_scope() as session:
            test_run = await session.get(TestRun, run_id)
            if not test_run:
                return None
            return {
                "id": test_run.id,
                "test_id": test_run.test_id,
                "provider": test_run.provider,
                "mode": test_run.mode,
                "status": test_run.status,
                "provider_call_id": test_run.provider_call_id,
                "transcript": test_run.transcript,
                "evaluation": test_run.evaluation,
                "created_at": test_run.created_at,
                "updated_at": test_run.updated_at,
            }
    
    async def list_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        async with session_scope() as session:
            statement = select(TestRun).order_by(TestRun.created_at.desc()).limit(limit)
            result = await session.exec(statement)
            runs = result.all()
            return [
                {
                    "id": run.id,
                    "test_id": run.test_id,
                    "provider": run.provider,
                    "mode": run.mode,
                    "status": run.status,
                    "provider_call_id": run.provider_call_id,
                    "transcript": run.transcript,
                    "evaluation": run.evaluation,
                    "created_at": run.created_at,
                    "updated_at": run.updated_at,
                }
                for run in runs
            ]
    
    async def update(
        self,
        run_id: str,
        status: Optional[str] = None,
        transcript: Optional[List[Dict[str, Any]]] = None,
        evaluation: Optional[Dict[str, Any]] = None,
        append_transcript: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        async with session_scope() as session:
            test_run = await session.get(TestRun, run_id)
            if not test_run:
                return False
            
            if status is not None:
                test_run.status = status
            
            if transcript is not None:
                test_run.transcript = transcript
            
            if evaluation is not None:
                test_run.evaluation = evaluation
            
            if append_transcript:
                test_run.append_transcript(append_transcript)
            
            test_run.touch()
            return True

"""Storage abstraction layer supporting both database and in-memory backends."""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from models.test_cases import TestCase, TurnExpectation


class TestCaseStore(ABC):
    """Abstract interface for test case storage."""
    
    @abstractmethod
    async def get(self, test_id: str) -> Optional[TestCase]:
        """Retrieve a test case by ID."""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[TestCase]:
        """List all test cases."""
        pass
    
    @abstractmethod
    async def upsert(self, test_case: TestCase) -> None:
        """Insert or update a test case."""
        pass
    
    @abstractmethod
    async def delete(self, test_id: str) -> bool:
        """Delete a test case. Returns True if deleted, False if not found."""
        pass


class TestRunStore(ABC):
    """Abstract interface for test run storage."""
    
    @abstractmethod
    async def create(
        self,
        test_id: str,
        provider: str,
        mode: str,
        provider_call_id: Optional[str] = None,
    ) -> str:
        """Create a new test run and return its ID."""
        pass
    
    @abstractmethod
    async def get(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a test run by ID."""
        pass
    
    @abstractmethod
    async def list_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent test runs."""
        pass
    
    @abstractmethod
    async def update(
        self,
        run_id: str,
        status: Optional[str] = None,
        transcript: Optional[List[Dict[str, Any]]] = None,
        evaluation: Optional[Dict[str, Any]] = None,
        append_transcript: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Update a test run. Returns True if updated, False if not found."""
        pass


class InMemoryTestCaseStore(TestCaseStore):
    """In-memory implementation of test case storage."""
    
    def __init__(self) -> None:
        self._data: Dict[str, TestCase] = {}
    
    async def get(self, test_id: str) -> Optional[TestCase]:
        return self._data.get(test_id)
    
    async def list_all(self) -> List[TestCase]:
        return sorted(self._data.values(), key=lambda tc: tc.test_id)
    
    async def upsert(self, test_case: TestCase) -> None:
        self._data[test_case.test_id] = test_case
    
    async def delete(self, test_id: str) -> bool:
        if test_id in self._data:
            del self._data[test_id]
            return True
        return False


class InMemoryTestRunStore(TestRunStore):
    """In-memory implementation of test run storage."""
    
    def __init__(self, max_transcript_size: int = 1000) -> None:
        self._data: Dict[str, Dict[str, Any]] = {}
        self._max_transcript_size = max_transcript_size
    
    async def create(
        self,
        test_id: str,
        provider: str,
        mode: str,
        provider_call_id: Optional[str] = None,
    ) -> str:
        run_id = str(uuid.uuid4())
        now = datetime.utcnow()
        self._data[run_id] = {
            "id": run_id,
            "test_id": test_id,
            "provider": provider,
            "mode": mode,
            "status": "initiated" if mode == "live" else "completed",
            "provider_call_id": provider_call_id,
            "transcript": [],
            "evaluation": None,
            "created_at": now,
            "updated_at": now,
        }
        return run_id
    
    async def get(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._data.get(run_id)
    
    async def list_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        runs = sorted(
            self._data.values(),
            key=lambda r: r["created_at"],
            reverse=True,
        )
        return runs[:limit]
    
    async def update(
        self,
        run_id: str,
        status: Optional[str] = None,
        transcript: Optional[List[Dict[str, Any]]] = None,
        evaluation: Optional[Dict[str, Any]] = None,
        append_transcript: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        if run_id not in self._data:
            return False
        
        run = self._data[run_id]
        
        if status is not None:
            run["status"] = status
        
        if transcript is not None:
            # Limit transcript size to prevent memory issues
            run["transcript"] = transcript[-self._max_transcript_size:]
        
        if evaluation is not None:
            run["evaluation"] = evaluation
        
        if append_transcript:
            combined = [*run["transcript"], *append_transcript]
            # Keep only the most recent entries
            run["transcript"] = combined[-self._max_transcript_size:]
        
        run["updated_at"] = datetime.utcnow()
        return True


# Global in-memory stores (singleton pattern for simple use)
_in_memory_test_case_store: Optional[InMemoryTestCaseStore] = None
_in_memory_test_run_store: Optional[InMemoryTestRunStore] = None


def get_in_memory_test_case_store() -> InMemoryTestCaseStore:
    """Get or create the global in-memory test case store."""
    global _in_memory_test_case_store
    if _in_memory_test_case_store is None:
        _in_memory_test_case_store = InMemoryTestCaseStore()
    return _in_memory_test_case_store


def get_in_memory_test_run_store() -> InMemoryTestRunStore:
    """Get or create the global in-memory test run store."""
    global _in_memory_test_run_store
    if _in_memory_test_run_store is None:
        from core.config import get_settings
        settings = get_settings()
        _in_memory_test_run_store = InMemoryTestRunStore(
            max_transcript_size=settings.max_transcript_size
        )
    return _in_memory_test_run_store

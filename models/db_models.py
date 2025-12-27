"""SQLModel ORM models backing persistent test cases and runs."""
from __future__ import annotations

from datetime import datetime
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from models.test_cases import TestCase, TurnExpectation


class TestCaseRecord(SQLModel, table=True):
    """Stored deterministic test script definition."""

    __tablename__ = "test_cases"

    test_id: str = Field(primary_key=True, index=True)
    persona: str
    turns: List[Dict[str, Any]] = Field(
        sa_column=Column(JSON, nullable=False), default_factory=list  # type: ignore[arg-type]
    )
    to_number: Optional[str] = Field(default=None)
    from_number: Optional[str] = Field(default=None)
    call_direction: str = Field(default="inbound")

    def to_domain(self) -> TestCase:
        """Convert ORM row to rich Pydantic model."""
        turn_models = [TurnExpectation(**turn_data) for turn_data in self.turns]
        return TestCase(
            test_id=self.test_id,
            persona=self.persona,
            turns=turn_models,
            to_number=self.to_number,
            from_number=self.from_number,
            call_direction=self.call_direction,
        )

    @classmethod
    def from_domain(cls, test_case: TestCase) -> "TestCaseRecord":
        return cls(
            test_id=test_case.test_id,
            persona=test_case.persona,
            turns=[turn.model_dump() for turn in test_case.turns],
            to_number=test_case.to_number,
            from_number=test_case.from_number,
            call_direction=test_case.call_direction.value,
        )


class TestRun(SQLModel, table=True):
    """Represents an execution instance against a test case."""

    __tablename__ = "test_runs"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    test_id: str = Field(foreign_key="test_cases.test_id")
    provider: str
    provider_call_id: Optional[str] = Field(default=None)
    mode: str = Field(default="simulation")
    status: str = Field(default="pending")
    transcript: List[Dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)  # type: ignore[arg-type]
    )
    evaluation: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON, nullable=True)  # type: ignore[arg-type]
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    def append_transcript(self, new_rows: List[Dict[str, Any]]) -> None:
        self.transcript = [*self.transcript, *new_rows]
        self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()

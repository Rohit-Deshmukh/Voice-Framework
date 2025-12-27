"""Request/response schemas for FastAPI endpoints."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TestRunMode(str, Enum):
    simulation = "simulation"
    live = "live"


class TranscriptRowModel(BaseModel):
    speaker: str = Field(..., description="Either 'user' or 'agent'")
    text: str
    step_order: Optional[int] = None
    timestamp: Optional[str] = None


class TestRunRequest(BaseModel):
    test_id: str
    provider: str = Field(default="twilio")
    to_number: Optional[str] = None
    from_number: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    mode: TestRunMode = Field(default=TestRunMode.simulation)


class TestRunResponse(BaseModel):
    run_id: str
    status: str
    provider_call_id: Optional[str] = None
    evaluation: Optional[Dict[str, Any]] = None


class WebhookEvent(BaseModel):
    test_run_id: str
    provider_payload: Dict[str, Any] = Field(default_factory=dict)
    transcript: List[TranscriptRowModel] = Field(default_factory=list)
    completed: bool = Field(default=False)


class TurnExpectationSchema(BaseModel):
    step_order: int
    user_input: str
    expected_agent_response_keywords: List[str]
    exact_match_required: bool


class TestCaseSchema(BaseModel):
    test_id: str
    persona: str
    turns: List[TurnExpectationSchema]
    to_number: Optional[str] = None
    from_number: Optional[str] = None
    call_direction: str = "inbound"  # inbound or outbound


class TestRunSummary(BaseModel):
    run_id: str
    test_id: str
    provider: str
    status: str
    mode: str
    created_at: datetime
    updated_at: datetime
    provider_call_id: Optional[str] = None
    evaluation: Optional[Dict[str, Any]] = None


class TestRunDetailResponse(TestRunSummary):
    transcript: List[TranscriptRowModel] = Field(default_factory=list)

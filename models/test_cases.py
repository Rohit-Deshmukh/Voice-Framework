"""Pydantic data models for deterministic voice test cases."""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Self


class CallDirection(str, Enum):
    """Direction of the phone call."""
    inbound = "inbound"  # User calls the AI agent
    outbound = "outbound"  # AI agent calls the user


class TurnExpectation(BaseModel):
    """Single conversational step definition for the simulator and evaluator."""

    step_order: int = Field(..., ge=1, description="1-based index for ordering the flow")
    user_input: str = Field(..., description="Prompt the simulator will speak")
    expected_agent_response_keywords: List[str] = Field(
        ..., description="Keywords the agent response must contain"
    )
    exact_match_required: bool = Field(
        False,
        description="Whether the agent response must match user_input exactly",
    )

    @field_validator("expected_agent_response_keywords")
    @classmethod
    def _strip_keywords(cls, keywords: List[str]) -> List[str]:  # noqa: D401
        """Ensure keywords are meaningful tokens."""
        cleaned_keywords = [keyword.strip() for keyword in keywords]
        if any(not keyword for keyword in cleaned_keywords):
            raise ValueError("Keywords cannot be empty or whitespace")
        return cleaned_keywords


class TestCase(BaseModel):
    """Ordered deterministic flow definition for a single test."""

    test_id: str = Field(..., description="Unique identifier for the test case")
    persona: str = Field(..., description="Simulator persona name or description")
    turns: List[TurnExpectation] = Field(..., description="Ordered turn expectations")
    
    # Call configuration
    to_number: Optional[str] = Field(
        default=None,
        description="Phone number to call (for outbound) or receiving the call (for inbound)"
    )
    from_number: Optional[str] = Field(
        default=None,
        description="Phone number making the call (for outbound) or agent's number (for inbound)"
    )
    call_direction: CallDirection = Field(
        default=CallDirection.inbound,
        description="Direction of call: 'inbound' (user calls agent) or 'outbound' (agent calls user)"
    )

    @model_validator(mode='after')
    def _validate_turn_order(self) -> Self:
        """Ensure steps are sequential without duplicates."""
        if not self.turns:
            raise ValueError("TestCase requires at least one turn expectation")
        expected_order = 1
        for turn in self.turns:
            if turn.step_order != expected_order:
                raise ValueError("turns must be sequential starting at 1")
            expected_order += 1
        return self

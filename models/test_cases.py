"""Pydantic data models for deterministic voice test cases."""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, validator


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

    @validator("expected_agent_response_keywords", each_item=True)
    def _strip_keywords(cls, keyword: str) -> str:  # noqa: D401
        """Ensure keywords are meaningful tokens."""
        cleaned = keyword.strip()
        if not cleaned:
            raise ValueError("Keywords cannot be empty or whitespace")
        return cleaned


class TestCase(BaseModel):
    """Ordered deterministic flow definition for a single test."""

    test_id: str = Field(..., description="Unique identifier for the test case")
    persona: str = Field(..., description="Simulator persona name or description")
    turns: List[TurnExpectation] = Field(..., description="Ordered turn expectations")

    @validator("turns")
    def _validate_turn_order(cls, turns: List[TurnExpectation]) -> List[TurnExpectation]:
        """Ensure steps are sequential without duplicates."""
        if not turns:
            raise ValueError("TestCase requires at least one turn expectation")
        expected_order = 1
        for turn in turns:
            if turn.step_order != expected_order:
                raise ValueError("turns must be sequential starting at 1")
            expected_order += 1
        return turns

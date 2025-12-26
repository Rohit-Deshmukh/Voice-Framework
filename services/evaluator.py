"""Evaluator that produces pass/fail judgments and summaries."""
from __future__ import annotations

from typing import Any, Dict, Optional, Protocol, Sequence

from models.test_cases import TestCase
from services.llm import LLMClientProtocol
from services.validation import TranscriptRow, validate_turn_by_turn


class SentimentClientProtocol(Protocol):
    async def summarize(self, transcript: Sequence[TranscriptRow]) -> str:
        ...


class RuleBasedSentimentClient:
    """Simple heuristic summarizer when no LLM is wired."""

    async def summarize(self, transcript: Sequence[TranscriptRow]) -> str:
        agent_lines = [row["text"] for row in transcript if row.get("speaker") == "agent"]
        if not agent_lines:
            return "Fail: agent never responded."
        negative_markers = ["angry", "upset", "refund", "complain"]
        joined = " ".join(agent_lines).lower()
        if any(marker in joined for marker in negative_markers):
            return "Fail: agent tone suggested frustration or refusal."
        return "Pass: agent maintained neutral or helpful tone."


class LLMSentimentClient:
    """Delegates scoring to a configured LLM for richer summaries."""

    def __init__(self, llm_client: LLMClientProtocol) -> None:
        self.llm_client = llm_client

    async def summarize(self, transcript: Sequence[TranscriptRow]) -> str:
        if not transcript:
            return "Fail: empty transcript."
        condensed = "\n".join(
            f"{row.get('speaker', 'unknown')}: {row.get('text', '')}" for row in transcript
        )
        prompt = (
            "You are a QA judge reviewing a contact center call. "
            "Decide PASS or FAIL based solely on agent helpfulness and policy adherence. "
            "Respond with 'Pass:' or 'Fail:' followed by a concise justification under 40 words. "
            f"Transcript:\n{condensed}\nJudgment:"
        )
        summary = await self.llm_client.generate(prompt)
        return summary.strip()


class EvaluatorService:
    """Runs sentiment plus zipper validation for a conversation."""

    def __init__(
        self,
        sentiment_client: Optional[SentimentClientProtocol] = None,
        llm_client: Optional[LLMClientProtocol] = None,
    ) -> None:
        if sentiment_client is not None:
            self.sentiment_client = sentiment_client
        elif llm_client is not None:
            self.sentiment_client = LLMSentimentClient(llm_client)
        else:
            self.sentiment_client = RuleBasedSentimentClient()

    async def evaluate(self, transcript: Sequence[TranscriptRow], test_case: TestCase) -> Dict[str, Any]:
        zipper_report = validate_turn_by_turn(transcript, test_case)
        sentiment_summary = await self.sentiment_client.summarize(transcript)
        overall_pass = zipper_report["overall_passed"]
        if overall_pass and sentiment_summary.lower().startswith("fail"):
            overall_pass = False
        return {
            "status": "pass" if overall_pass else "fail",
            "sentiment_summary": sentiment_summary,
            "zipper_report": zipper_report,
        }

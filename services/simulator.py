"""Simulator agent that roleplays the customer using deterministic scripts."""
from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Protocol

from models.test_cases import TestCase, TurnExpectation
from services.llm import LLMClientProtocol, NoopLLMClient


TranscriptRow = Dict[str, Any]


class AgentResponderProtocol(Protocol):
    async def respond(self, user_text: str, turn: TurnExpectation) -> str:
        ...


class DeterministicAgentResponder:
    """Returns the expected keywords as the agent response (ideal-pass simulation)."""

    async def respond(self, _: str, turn: TurnExpectation) -> str:
        return " ".join(turn.expected_agent_response_keywords)


class SimulatorAgent:
    """Walk a TestCase turn-by-turn and collect a transcript."""

    def __init__(
        self,
        llm_client: Optional[LLMClientProtocol] = None,
        agent_responder: Optional[AgentResponderProtocol] = None,
        naturalize_user_prompts: bool = False,
        disfluency_rate: float = 0.0,
    ) -> None:
        self.llm_client = llm_client or NoopLLMClient()
        self.agent_responder = agent_responder or DeterministicAgentResponder()
        self.naturalize_user_prompts = naturalize_user_prompts
        self.disfluency_rate = max(0.0, min(disfluency_rate, 1.0))

    async def run(self, test_case: TestCase) -> List[TranscriptRow]:
        transcript: List[TranscriptRow] = []
        needs_steer = False
        last_agent_response: Optional[str] = None

        for turn in test_case.turns:
            user_text = await self._render_user_prompt(test_case, turn)
            if needs_steer:
                user_text = await self._generate_steer_text(test_case, turn, last_agent_response)
            user_text = self._inject_disfluencies(user_text)
            transcript.append(
                {
                    "speaker": "user",
                    "text": user_text,
                    "step_order": turn.step_order,
                }
            )
            agent_response = await self.agent_responder.respond(user_text, turn)
            transcript.append(
                {
                    "speaker": "agent",
                    "text": agent_response,
                    "step_order": turn.step_order,
                }
            )
            needs_steer = not self._agent_matched_expectation(
                agent_response,
                turn.expected_agent_response_keywords,
                turn.exact_match_required,
            )
            last_agent_response = agent_response

        return transcript

    async def _render_user_prompt(self, test_case: TestCase, turn: TurnExpectation) -> str:
        """Optionally let the LLM naturalize the scripted line."""

        if not self.naturalize_user_prompts or isinstance(self.llm_client, NoopLLMClient):
            return turn.user_input

        prompt = (
            "You are role-playing a caller in a QA test. "
            f"Adopt the persona '{test_case.persona}'. "
            "Restate the following line in your own words while preserving intent: "
            f"'{turn.user_input}'. Keep it under 20 words."
        )
        candidate = await self.llm_client.generate(prompt)
        return candidate or turn.user_input

    async def _generate_steer_text(
        self,
        test_case: TestCase,
        turn: TurnExpectation,
        agent_response: Optional[str],
    ) -> str:
        """Use the LLM to nudge the agent back to the scripted step."""

        steer_prompt = (
            "You are a QA caller ensuring the agent follows the script. "
            f"Stay in persona '{test_case.persona}'. "
            "Craft a short sentence that politely redirects the agent toward: "
            f"'{turn.user_input}'. The agent previously responded with: "
            f"'{agent_response or 'NO RESPONSE'}'."
        )
        return await self.llm_client.generate(steer_prompt)

    def _inject_disfluencies(self, text: str) -> str:
        """Optionally add filler words to mimic more natural callers."""

        if not self.disfluency_rate or not text.strip():
            return text
        if random.random() > self.disfluency_rate:
            return text

        fillers = ["um", "uh", "you know", "I mean", "like"]
        words = text.split()
        insert_at = random.randint(0, len(words)) if words else 0
        filler = random.choice(fillers)
        words.insert(insert_at, filler)
        return " ".join(words)

    @staticmethod
    def _agent_matched_expectation(
        agent_text: str,
        keywords: List[str],
        exact_match: bool,
    ) -> bool:
        normalized = " ".join(agent_text.lower().strip().split())
        if exact_match:
            target = " ".join(keyword.lower().strip() for keyword in keywords)
            return normalized == target
        return all(keyword.lower() in normalized for keyword in keywords)

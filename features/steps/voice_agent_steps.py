"""Behave step definitions for voice agent testing."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from behave import given, when, then
from behave.runner import Context

from models.test_cases import TestCase, TurnExpectation
from services.simulator import SimulatorAgent
from services.evaluator import EvaluatorService
from services.llm import NoopLLMClient


@given('a test case with id "{test_id}"')
def step_given_test_case(context: Context, test_id: str) -> None:
    """Initialize a test case with the given ID."""
    context.test_id = test_id
    context.turns: List[TurnExpectation] = []
    context.persona = "Test Persona"


@given('the persona is "{persona}"')
def step_given_persona(context: Context, persona: str) -> None:
    """Set the persona for the test case."""
    context.persona = persona


@given('turn {step_order:d} where user says "{user_input}"')
def step_given_turn_user_input(context: Context, step_order: int, user_input: str) -> None:
    """Add a turn with user input."""
    if not hasattr(context, 'current_turn'):
        context.current_turn = {}
    context.current_turn['step_order'] = step_order
    context.current_turn['user_input'] = user_input


@given('the agent should respond with keywords "{keywords}"')
def step_given_agent_keywords(context: Context, keywords: str) -> None:
    """Define expected agent response keywords."""
    if not hasattr(context, 'current_turn'):
        context.current_turn = {}
    keyword_list = [k.strip() for k in keywords.split(',')]
    context.current_turn['expected_agent_response_keywords'] = keyword_list
    context.current_turn['exact_match_required'] = False
    
    # Create the turn expectation and add to turns list
    turn = TurnExpectation(**context.current_turn)
    context.turns.append(turn)
    context.current_turn = {}


@given('exact match is required')
def step_given_exact_match(context: Context) -> None:
    """Mark that exact match is required for the current turn."""
    if hasattr(context, 'current_turn'):
        context.current_turn['exact_match_required'] = True


@when('the test is executed')
def step_when_test_executed(context: Context) -> None:
    """Execute the test case simulation."""
    # Build the test case
    test_case = TestCase(
        test_id=context.test_id,
        persona=context.persona,
        turns=context.turns
    )
    
    # Run simulation
    simulator = SimulatorAgent(
        llm_client=NoopLLMClient(),
        naturalize_user_prompts=False,
        disfluency_rate=0.0
    )
    
    # Run async simulation using asyncio.run for proper lifecycle management
    async def run_test():
        transcript = await simulator.run(test_case)
        evaluator = EvaluatorService(llm_client=NoopLLMClient())
        evaluation = await evaluator.evaluate(transcript, test_case)
        return transcript, evaluation
    
    context.transcript, context.evaluation = asyncio.run(run_test())
    context.test_case = test_case


@then('the test should pass')
def step_then_test_passes(context: Context) -> None:
    """Verify that the test passed."""
    status = context.evaluation.get('status')
    zipper_report = context.evaluation.get('zipper_report', {})
    overall_passed = zipper_report.get('overall_passed', False)
    
    assert status == 'pass' and overall_passed, \
        f"Test failed: status={status}, zipper_report={zipper_report}"


@then('the test should fail')
def step_then_test_fails(context: Context) -> None:
    """Verify that the test failed."""
    status = context.evaluation.get('status')
    zipper_report = context.evaluation.get('zipper_report', {})
    overall_passed = zipper_report.get('overall_passed', True)
    
    assert status != 'pass' or not overall_passed, \
        "Test was expected to fail but passed"


@then('{step_count:d} turns should be executed')
def step_then_turn_count(context: Context, step_count: int) -> None:
    """Verify the number of turns executed."""
    # Transcript has 2 entries per turn (user + agent)
    assert len(context.transcript) == step_count * 2, \
        f"Expected {step_count * 2} transcript entries, got {len(context.transcript)}"


@then('turn {step_order:d} should pass')
def step_then_turn_passes(context: Context, step_order: int) -> None:
    """Verify that a specific turn passed."""
    zipper_report = context.evaluation.get('zipper_report', {})
    steps = zipper_report.get('steps', [])
    turn_result = None
    for step in steps:
        if step.get('step_order') == step_order:
            turn_result = step
            break
    
    assert turn_result and turn_result.get('passed'), \
        f"Turn {step_order} did not pass: {turn_result}"


@then('turn {step_order:d} should fail')
def step_then_turn_fails(context: Context, step_order: int) -> None:
    """Verify that a specific turn failed."""
    zipper_report = context.evaluation.get('zipper_report', {})
    steps = zipper_report.get('steps', [])
    turn_result = None
    for step in steps:
        if step.get('step_order') == step_order:
            turn_result = step
            break
    
    assert turn_result and not turn_result.get('passed'), \
        f"Turn {step_order} was expected to fail but passed"


@then('the transcript should contain "{text}"')
def step_then_transcript_contains(context: Context, text: str) -> None:
    """Verify that the transcript contains specific text."""
    transcript_text = ' '.join(row['text'] for row in context.transcript)
    assert text.lower() in transcript_text.lower(), \
        f"Transcript does not contain '{text}'"

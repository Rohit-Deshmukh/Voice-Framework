"""FastAPI application exposing simulation and webhook endpoints."""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, Path

from api.deps import require_api_key
from api.schemas import (
    TestCaseSchema,
    TurnExpectationSchema,
    TestRunDetailResponse,
    TestRunMode,
    TestRunRequest,
    TestRunResponse,
    TestRunSummary,
    WebhookEvent,
)
from core.config import Settings, get_settings
from core.database import init_db
from core.storage import (
    TestCaseStore,
    TestRunStore,
    get_in_memory_test_case_store,
    get_in_memory_test_run_store,
)
from core.telephony import SIPTrunkProvider, TelephonyProvider, TwilioProvider, ZoomPhoneProvider
from models.test_cases import TestCase
from services.evaluator import EvaluatorService
from services.llm import build_llm_client
from services.simulator import SimulatorAgent

settings = get_settings()

# Only build LLM client if enabled (reduces memory and startup time)
llm_client = build_llm_client(settings) if settings.enable_llm else None

app = FastAPI(
    title="Voice Agent Testing",
    version="0.1.0",
    dependencies=[Depends(require_api_key)],
)

# Disable LLM features if not enabled (lighter resource usage)
simulator = SimulatorAgent(
    llm_client=llm_client,
    naturalize_user_prompts=settings.enable_llm,
    disfluency_rate=0.15 if settings.enable_llm else 0.0,
)
evaluator = EvaluatorService(llm_client=llm_client)


def get_test_case_store() -> TestCaseStore:
    """Get the appropriate test case store based on configuration."""
    if settings.use_database:
        # Import here to avoid circular dependency
        from core.database_storage import DatabaseTestCaseStore
        return DatabaseTestCaseStore()
    return get_in_memory_test_case_store()


def get_test_run_store() -> TestRunStore:
    """Get the appropriate test run store based on configuration."""
    if settings.use_database:
        # Import here to avoid circular dependency
        from core.database_storage import DatabaseTestRunStore
        return DatabaseTestRunStore()
    return get_in_memory_test_run_store()


@app.on_event("startup")
async def _startup() -> None:
    await init_db()
    
    # Auto-load sample test cases for in-memory storage
    if not settings.use_database:
        from scripts.seed_test_cases import SAMPLE_TEST_CASES
        test_case_store = get_in_memory_test_case_store()
        for case in SAMPLE_TEST_CASES:
            await test_case_store.upsert(case)
        print(f"✓ Auto-loaded {len(SAMPLE_TEST_CASES)} sample test cases to in-memory storage.")


def _resolve_provider(settings: Settings, provider_name: str) -> TelephonyProvider:
    provider_name = provider_name.lower()
    if provider_name == "twilio":
        if not (settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_default_from):
            raise HTTPException(status_code=500, detail="Twilio credentials are not configured")
        return TwilioProvider(
            account_sid=settings.twilio_account_sid,
            auth_token=settings.twilio_auth_token,
            default_from_number=settings.twilio_default_from,
        )
    if provider_name == "zoom_phone":
        return ZoomPhoneProvider()
    if provider_name == "sip_trunk":
        return SIPTrunkProvider()
    raise HTTPException(status_code=400, detail=f"Unsupported provider '{provider_name}'")


def _serialize_test_case(test_case: TestCase) -> TestCaseSchema:
    return TestCaseSchema(
        test_id=test_case.test_id,
        persona=test_case.persona,
        turns=[TurnExpectationSchema(**turn.model_dump()) for turn in test_case.turns],
        to_number=test_case.to_number,
        from_number=test_case.from_number,
        call_direction=test_case.call_direction.value,
    )


def _serialize_test_run(run: Dict[str, Any]) -> TestRunSummary:
    return TestRunSummary(
        run_id=run["id"],
        test_id=run["test_id"],
        provider=run["provider"],
        status=run["status"],
        mode=run["mode"],
        created_at=run["created_at"],
        updated_at=run["updated_at"],
        provider_call_id=run.get("provider_call_id"),
        evaluation=run.get("evaluation"),
    )


@app.get("/testcases", response_model=List[TestCaseSchema])
async def list_test_cases(
    test_case_store: TestCaseStore = Depends(get_test_case_store),
) -> List[TestCaseSchema]:
    test_cases = await test_case_store.list_all()
    return [_serialize_test_case(tc) for tc in test_cases]


@app.get("/testruns", response_model=List[TestRunSummary])
async def list_test_runs(
    limit: int = 10,
    test_run_store: TestRunStore = Depends(get_test_run_store),
) -> List[TestRunSummary]:
    limit = max(1, min(limit, 100))
    runs = await test_run_store.list_recent(limit=limit)
    return [_serialize_test_run(run) for run in runs]


@app.get("/testruns/{run_id}", response_model=TestRunDetailResponse)
async def get_test_run(
    run_id: str,
    test_run_store: TestRunStore = Depends(get_test_run_store),
) -> TestRunDetailResponse:
    test_run = await test_run_store.get(run_id)
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    summary = _serialize_test_run(test_run)
    return TestRunDetailResponse(**summary.model_dump(), transcript=test_run["transcript"])


@app.post("/test/run", response_model=TestRunResponse)
async def run_test_case(
    payload: TestRunRequest,
    test_case_store: TestCaseStore = Depends(get_test_case_store),
    test_run_store: TestRunStore = Depends(get_test_run_store),
    settings: Settings = Depends(get_settings),
) -> TestRunResponse:
    test_case = await test_case_store.get(payload.test_id)
    if not test_case:
        raise HTTPException(status_code=404, detail=f"Test case '{payload.test_id}' not found")
    
    mode = "live" if payload.mode == TestRunMode.live else "simulation"
    run_id = await test_run_store.create(
        test_id=test_case.test_id,
        provider=payload.provider,
        mode=mode,
    )

    if payload.mode == TestRunMode.live:
        # Determine phone numbers: payload overrides test case, test case overrides settings
        to_number = payload.to_number or test_case.to_number
        from_number = payload.from_number or test_case.from_number or settings.twilio_default_from
        
        if not to_number:
            raise HTTPException(
                status_code=400,
                detail="to_number is required for live mode (provide in request or feature file)"
            )
        
        provider = _resolve_provider(settings, payload.provider)
        call_result = await provider.initiate_call(
            to_number=to_number,
            from_number=from_number,
            test_case_id=test_case.test_id,
            metadata={
                **payload.metadata,
                "call_direction": test_case.call_direction.value,
            },
        )
        provider_call_id = call_result.get("provider_call_id")
        await test_run_store.update(run_id, status="initiated")
        
        test_run = await test_run_store.get(run_id)
        return TestRunResponse(
            run_id=run_id,
            status=test_run["status"] if test_run else "initiated",
            provider_call_id=provider_call_id,
        )

    transcript = await simulator.run(test_case)
    evaluation = await evaluator.evaluate(transcript, test_case)
    await test_run_store.update(
        run_id,
        status="completed",
        transcript=transcript,
        evaluation=evaluation,
    )
    return TestRunResponse(
        run_id=run_id,
        status="completed",
        provider_call_id=None,
        evaluation=evaluation,
    )


@app.post("/webhooks/voice/{provider}")
async def provider_webhook(
    event: WebhookEvent,
    provider: str = Path(..., description="Provider slug"),
    test_case_store: TestCaseStore = Depends(get_test_case_store),
    test_run_store: TestRunStore = Depends(get_test_run_store),
    settings: Settings = Depends(get_settings),
) -> Dict[str, object]:
    provider_instance = _resolve_provider(settings, provider)
    normalized_event = await provider_instance.parse_webhook_event(event.provider_payload)

    test_run = await test_run_store.get(event.test_run_id)
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")

    transcript_rows = [row.model_dump() for row in event.transcript]
    if transcript_rows:
        await test_run_store.update(event.test_run_id, append_transcript=transcript_rows)

    response_payload: Dict[str, object] = {"normalized_event": normalized_event}

    if event.completed:
        test_case = await test_case_store.get(test_run["test_id"])
        if not test_case:
            raise HTTPException(status_code=404, detail=f"Test case '{test_run['test_id']}' not found")
        
        # Refresh test_run to get updated transcript
        test_run = await test_run_store.get(event.test_run_id)
        if test_run:
            evaluation = await evaluator.evaluate(test_run["transcript"], test_case)
            await test_run_store.update(
                event.test_run_id,
                status="completed",
                evaluation=evaluation,
            )
            response_payload["evaluation"] = evaluation

    return response_payload

"""FastAPI application exposing simulation and webhook endpoints."""
from __future__ import annotations

from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException, Path
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

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
from core.database import get_session, init_db
from core.telephony import SIPTrunkProvider, TelephonyProvider, TwilioProvider, ZoomPhoneProvider
from models.db_models import TestCaseRecord, TestRun
from services.evaluator import EvaluatorService
from services.llm import build_llm_client
from services.simulator import SimulatorAgent

settings = get_settings()
llm_client = build_llm_client(settings)

app = FastAPI(
    title="Voice Agent Testing",
    version="0.1.0",
    dependencies=[Depends(require_api_key)],
)
simulator = SimulatorAgent(llm_client=llm_client, naturalize_user_prompts=True, disfluency_rate=0.15)
evaluator = EvaluatorService(llm_client=llm_client)


@app.on_event("startup")
async def _startup() -> None:
    await init_db()


async def _fetch_test_case(session: AsyncSession, test_id: str) -> TestCaseRecord:
    statement = select(TestCaseRecord).where(TestCaseRecord.test_id == test_id)
    result = await session.exec(statement)
    record = result.one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail=f"Test case '{test_id}' not found")
    return record


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


def _serialize_test_case(record: TestCaseRecord) -> TestCaseSchema:
    return TestCaseSchema(
        test_id=record.test_id,
        persona=record.persona,
        turns=[TurnExpectationSchema(**turn) for turn in record.turns],
    )


def _serialize_test_run(run: TestRun) -> TestRunSummary:
    return TestRunSummary(
        run_id=run.id,
        test_id=run.test_id,
        provider=run.provider,
        status=run.status,
        mode=run.mode,
        created_at=run.created_at,
        updated_at=run.updated_at,
        provider_call_id=run.provider_call_id,
        evaluation=run.evaluation,
    )


@app.get("/testcases", response_model=List[TestCaseSchema])
async def list_test_cases(session: AsyncSession = Depends(get_session)) -> List[TestCaseSchema]:
    result = await session.exec(select(TestCaseRecord).order_by(TestCaseRecord.test_id))
    records = result.all()
    return [_serialize_test_case(record) for record in records]


@app.get("/testruns", response_model=List[TestRunSummary])
async def list_test_runs(
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
) -> List[TestRunSummary]:
    limit = max(1, min(limit, 100))
    statement = select(TestRun).order_by(TestRun.created_at.desc()).limit(limit)
    result = await session.exec(statement)
    runs = result.all()
    return [_serialize_test_run(run) for run in runs]


@app.get("/testruns/{run_id}", response_model=TestRunDetailResponse)
async def get_test_run(
    run_id: str,
    session: AsyncSession = Depends(get_session),
) -> TestRunDetailResponse:
    test_run = await session.get(TestRun, run_id)
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    summary = _serialize_test_run(test_run)
    return TestRunDetailResponse(**summary.dict(), transcript=test_run.transcript)


@app.post("/test/run", response_model=TestRunResponse)
async def run_test_case(
    payload: TestRunRequest,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> TestRunResponse:
    record = await _fetch_test_case(session, payload.test_id)
    test_case = record.to_domain()
    test_run = TestRun(
        test_id=test_case.test_id,
        provider=payload.provider,
        mode=payload.mode.value,
        status="initiated" if payload.mode == TestRunMode.live else "completed",
    )

    if payload.mode == TestRunMode.live:
        if not payload.to_number:
            raise HTTPException(status_code=400, detail="to_number is required for live mode")
        provider = _resolve_provider(settings, payload.provider)
        call_result = await provider.initiate_call(
            to_number=payload.to_number or "",  # real number required in live mode
            from_number=payload.from_number or settings.twilio_default_from,
            test_case_id=test_case.test_id,
            metadata=payload.metadata,
        )
        test_run.provider_call_id = call_result.get("provider_call_id")
        session.add(test_run)
        await session.commit()
        return TestRunResponse(
            run_id=test_run.id,
            status=test_run.status,
            provider_call_id=test_run.provider_call_id,
        )

    transcript = await simulator.run(test_case)
    evaluation = await evaluator.evaluate(transcript, test_case)
    test_run.transcript = transcript
    test_run.evaluation = evaluation
    test_run.touch()
    session.add(test_run)
    await session.commit()
    return TestRunResponse(
        run_id=test_run.id,
        status=test_run.status,
        provider_call_id=test_run.provider_call_id,
        evaluation=evaluation,
    )


@app.post("/webhooks/voice/{provider}")
async def provider_webhook(
    event: WebhookEvent,
    provider: str = Path(..., description="Provider slug"),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> Dict[str, object]:
    provider_instance = _resolve_provider(settings, provider)
    normalized_event = await provider_instance.parse_webhook_event(event.provider_payload)

    result = await session.exec(select(TestRun).where(TestRun.id == event.test_run_id))
    test_run = result.one_or_none()
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")

    transcript_rows = [row.dict() for row in event.transcript]
    if transcript_rows:
        test_run.append_transcript(transcript_rows)

    response_payload: Dict[str, object] = {"normalized_event": normalized_event}

    if event.completed:
        test_case_record = await _fetch_test_case(session, test_run.test_id)
        evaluation = await evaluator.evaluate(test_run.transcript, test_case_record.to_domain())
        test_run.evaluation = evaluation
        test_run.status = "completed"
        test_run.touch()
        response_payload["evaluation"] = evaluation

    session.add(test_run)
    await session.commit()
    return response_payload

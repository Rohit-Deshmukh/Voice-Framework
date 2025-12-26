"""Streamlit dashboard for orchestrating deterministic voice QA runs."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import streamlit as st
from httpx import HTTPError

from services.api_client import VoiceFrameworkClient

DEFAULT_API_BASE_URL = os.getenv("VOICE_API_BASE_URL", "http://localhost:8000")
DEFAULT_API_KEY = os.getenv("VOICE_API_KEY", "")
DEFAULT_API_KEY_HEADER = os.getenv("VOICE_API_KEY_HEADER", "x-api-key")

st.set_page_config(page_title="Voice Agent QA Deck", page_icon="🎙️", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&display=swap');
    .stApp {
        font-family: 'Space Grotesk', sans-serif;
        background: radial-gradient(circle at top, #10162F 0%, #05060C 70%);
        color: #EFF2FF;
    }
    .metric-card {
        padding: 1rem 1.5rem;
        border-radius: 18px;
        background: rgba(16, 22, 47, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .metric-label {
        font-size: 0.85rem;
        letter-spacing: 0.05em;
        color: #9EA5C3;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #7EF5C4;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=30)
def load_test_cases(base_url: str, api_key: str, api_key_header: str) -> List[Dict[str, Any]]:
    client = VoiceFrameworkClient(
        base_url,
        api_key=api_key or None,
        api_key_header_name=api_key_header,
    )
    return client.list_test_cases()


@st.cache_data(ttl=15)
def load_recent_runs(
    base_url: str,
    api_key: str,
    api_key_header: str,
    limit: int,
) -> List[Dict[str, Any]]:
    client = VoiceFrameworkClient(
        base_url,
        api_key=api_key or None,
        api_key_header_name=api_key_header,
    )
    return client.list_test_runs(limit=limit)


def render_zipper_report(report: Dict[str, Any]) -> None:
    steps = report.get("steps", [])
    for step in steps:
        status_icon = "✅" if step.get("passed") else "❌"
        with st.expander(f"Step {step.get('step_order')}: {status_icon}", expanded=not step.get("passed")):
            cols = st.columns(2)
            cols[0].markdown(f"**Expected user:** {step.get('expected_user_input')}")
            cols[0].markdown(f"**Actual user:** {step.get('actual_user_input') or '—'}")
            cols[1].markdown(
                f"**Agent response:** {step.get('agent_response') or '—'}"
            )
            cols[1].markdown(
                f"**Keywords:** {', '.join(step.get('expected_keywords', []))}"
            )
            if not step.get("passed"):
                st.warning(step.get("details") or "Validation failed.")


with st.sidebar:
    st.title("Control Tower")
    base_url = st.text_input("API Base URL", value=DEFAULT_API_BASE_URL)
    api_key = st.text_input("API Key", value=DEFAULT_API_KEY, type="password")
    api_key_header = st.text_input("API Key Header", value=DEFAULT_API_KEY_HEADER)
    provider = st.selectbox("Telephony Provider", options=["twilio", "zoom_phone", "sip_trunk"])
    default_mode = st.radio("Mode", options=["simulation", "live"], index=0)
    to_number = st.text_input("To Number (live)")
    from_number = st.text_input("From Number (optional)")
    refresh_trigger = st.button("🔄 Refresh Catalog")

st.title("Voice Agent QA Deck")

client = VoiceFrameworkClient(
    base_url,
    api_key=api_key or None,
    api_key_header_name=api_key_header or "x-api-key",
)

try:
    if refresh_trigger:
        load_test_cases.clear()
        load_recent_runs.clear()
    test_cases = load_test_cases(base_url, api_key, api_key_header)
except HTTPError as exc:
    st.error(f"Failed to load test cases: {exc}")
    st.stop()

if not test_cases:
    st.info("No test cases found. Run `python scripts/seed_test_cases.py` first.")
    st.stop()

selected_case = st.selectbox(
    "Select Test Case",
    options=[case["test_id"] for case in test_cases],
    format_func=lambda tid: next(case["persona"] for case in test_cases if case["test_id"] == tid),
)
current_case = next(case for case in test_cases if case["test_id"] == selected_case)

st.subheader("Script Blueprint")
turn_rows = [
    {
        "Step": turn["step_order"],
        "User Prompt": turn["user_input"],
        "Keywords": ", ".join(turn["expected_agent_response_keywords"]),
        "Exact?": "Yes" if turn["exact_match_required"] else "No",
    }
    for turn in current_case["turns"]
]
st.dataframe(turn_rows, hide_index=True, use_container_width=True)

with st.form("run-form"):
    st.markdown("### Execute Test")
    mode = st.radio("Execution Mode", options=["simulation", "live"], index=0 if default_mode == "simulation" else 1)
    metadata_input = st.text_area("Metadata JSON (optional)", value="{}")
    submitted = st.form_submit_button("Launch Run", use_container_width=True)

run_result: Dict[str, Any] | None = None
if submitted:
    metadata: Dict[str, Any] = {}
    if metadata_input.strip():
        try:
            metadata = json.loads(metadata_input)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Metadata JSON invalid: {exc}")
            metadata = {}
    try:
        payload = {
            "test_id": selected_case,
            "provider": provider,
            "mode": mode,
            "metadata": metadata,
        }
        can_execute = True
        if mode == "live":
            if not to_number:
                st.error("Live mode requires a destination number.")
                can_execute = False
            else:
                payload["to_number"] = to_number
                if from_number:
                    payload["from_number"] = from_number
        if can_execute:
            run_result = client.run_test_case(**payload)
            st.success(f"Run {run_result['run_id']} submitted ({run_result['status']}).")
            load_recent_runs.clear()
    except HTTPError as exc:  # noqa: BLE001
        st.error(f"Failed to start run: {exc}")

if run_result and run_result.get("evaluation"):
    evaluation = run_result["evaluation"]
    zipper_report = evaluation.get("zipper_report", {})
    metrics = zipper_report.get("metrics", {})
    zipper_steps = zipper_report.get("steps", [])
    steps_passed = metrics.get("steps_passed")
    total_steps = metrics.get("total_steps")
    if steps_passed is None:
        steps_passed = sum(1 for step in zipper_steps if step.get("passed"))
    if total_steps is None:
        total_steps = len(zipper_steps)
    coverage_pct = metrics.get("coverage")
    coverage_display = f"{coverage_pct * 100:.0f}%" if coverage_pct is not None else "—"
    cols = st.columns(3)
    cols[0].markdown(
        "<div class='metric-card'><div class='metric-label'>Status</div>"
        f"<div class='metric-value'>{evaluation['status'].upper()}</div></div>",
        unsafe_allow_html=True,
    )
    sentiment_headline = evaluation.get("sentiment_summary", "Pass").split(":")[0]
    cols[1].markdown(
        "<div class='metric-card'><div class='metric-label'>Sentiment</div>"
        f"<div class='metric-value'>{sentiment_headline}</div></div>",
        unsafe_allow_html=True,
    )
    cols[2].markdown(
        "<div class='metric-card'><div class='metric-label'>Script Coverage</div>"
        f"<div class='metric-value'>{coverage_display} ({steps_passed}/{total_steps})</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("### Turn-by-Turn Validation")
    render_zipper_report(zipper_report)

st.markdown("### Recent Runs")
try:
    recent_runs = load_recent_runs(base_url, api_key, api_key_header, limit=5)
    if recent_runs:
        st.table(
            [
                {
                    "Run": run["run_id"],
                    "Test": run["test_id"],
                    "Status": run["status"],
                    "Mode": run["mode"],
                    "Provider": run["provider"],
                    "Updated": run["updated_at"],
                }
                for run in recent_runs
            ]
        )

        selected_run_id = st.selectbox(
            "Inspect run details",
            options=["(none)"] + [run["run_id"] for run in recent_runs],
        )
        if selected_run_id != "(none)":
            try:
                detail = client.get_test_run(selected_run_id)
                st.markdown(f"#### Transcript for {selected_run_id}")
                st.dataframe(detail.get("transcript", []), use_container_width=True)
                if detail.get("evaluation"):
                    st.markdown("#### Evaluation Snapshot")
                    render_zipper_report(detail["evaluation"].get("zipper_report", {}))
            except HTTPError as exc:  # noqa: BLE001
                st.error(f"Failed to load run detail: {exc}")
    else:
        st.caption("No runs yet. Launch a simulation above.")
except HTTPError as exc:  # noqa: BLE001
    st.error(f"Failed to load recent runs: {exc}")
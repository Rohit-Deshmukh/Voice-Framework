# Voice-Framework

Deterministic end-to-end testing harness for voice agents. The stack mirrors the original Next.js/Twilio workflow but runs entirely in Python (FastAPI + SQLModel) with optional LLM assist for simulator steering and evaluation.

## Features
- Modular layout (`core`, `api`, `models`, `services`, `scripts`) for clean separation of concerns.
- Telephony abstraction (`TelephonyProvider`) with a concrete Twilio implementation and placeholders for Zoom Phone / SIP trunks.
- Rich Pydantic models for scripted turn-by-turn expectations to enforce sequential logic.
- Simulator service that iterates through a `TestCase`, optionally naturalizing user prompts and steering on deviations via LLM.
- Evaluator service that performs zipper validation plus sentiment/QA scoring (LLM-backed when available).
- FastAPI endpoints for running simulations or live calls and processing provider webhooks.
- **NEW: Cucumber-style feature files** - Write test scenarios in natural language using Gherkin syntax for better readability and collaboration.

## Getting Started
1. **Create a virtual environment**
	```bash
	python -m venv .venv
	source .venv/bin/activate
	```
2. **Install dependencies**
	```bash
	pip install -r requirements.txt
	# For feature file support (optional but recommended)
	pip install -r requirements-features.txt
	```
3. **Configure environment variables** (create a `.env` file or export the vars)
	```bash
	DATABASE_URL=sqlite+aiosqlite:///./voice_framework.db
	TWILIO_ACCOUNT_SID=...
	TWILIO_AUTH_TOKEN=...
	TWILIO_DEFAULT_FROM=+15555555555
	VOICE_API_KEY=super-secret-token
	VOICE_API_KEY_HEADER=x-api-key
	OPENAI_API_KEY=...
	ANTHROPIC_API_KEY=...
	```
	Only set the provider keys you intend to use. The app falls back to deterministic/no-op behavior when keys are absent.
4. **Seed sample deterministic scripts**
	```bash
	python scripts/seed_test_cases.py
	```
5. **Run the API**
	```bash
	uvicorn api.main:app --reload
	```
6. **Trigger a simulation**
	```bash
	curl -X POST http://localhost:8000/test/run \
	  -H "Content-Type: application/json" \
	  -d '{"test_id":"billing_inquiry_v1","provider":"twilio","mode":"simulation"}'
	```

## Testing

### Running Cucumber-Style Feature Files (Recommended)
Write test scenarios in natural language using Gherkin syntax:
```bash
# Run all feature files
python scripts/run_features.py

# Or use behave directly
behave features/
```

See [docs/FEATURE_FILES_GUIDE.md](docs/FEATURE_FILES_GUIDE.md) for details on writing feature files.

### Running Python Tests
Run the automated test suite:
```bash
pytest
```

### Loading Feature Files into Database
Convert feature files to test cases in the database:
```bash
python scripts/load_features.py
```

## API Surface
- `GET /testcases` &mdash; Returns all scripted personas/flows with ordered turn expectations.
- `POST /test/run` &mdash; Launches a deterministic simulation or a live provider call (requires `to_number` for live mode).
- `GET /testruns?limit=10` &mdash; Lists the most recent executions along with evaluation metadata.
- `GET /testruns/{run_id}` &mdash; Retrieves a full transcript plus zipper report for a specific run.
- `POST /webhooks/voice/{provider}` &mdash; Unified webhook receiver that normalizes provider payloads, appends transcript rows, and triggers evaluation upon completion.

Responses include per-step zipper results highlighting exact failures (e.g., missing keywords) plus an overall pass/fail sentiment summary.

## Scripts
- `scripts/seed_test_cases.py` &mdash; Inserts baseline deterministic scripts for local development. Extend this file or swap in SQL migrations for production workflows.
- `scripts/run_features.py` &mdash; Executes Cucumber-style feature files using behave. Run with no arguments to execute all feature files.
- `scripts/load_features.py` &mdash; Parses feature files and loads them as test cases into the database for API-based execution.

## Streamlit Dashboard
Launch the reviewer console to orchestrate runs and inspect zipper outcomes:

```bash
VOICE_API_BASE_URL=http://localhost:8000 \
VOICE_API_KEY=super-secret-token \
VOICE_API_KEY_HEADER=x-api-key \
streamlit run streamlit_app.py
```

Capabilities:
- Browse all scripted personas and view their ordered turn expectations.
- Fire simulations or live tests without leaving the UI (live mode enforces `to_number`).
- Visualize zipper results with expandable per-turn diagnostics.
- Inspect recent runs, drill into transcripts, and compare evaluation snapshots.

## Authentication
- Every API call (including Streamlit) must include the configured API key header when `VOICE_API_KEY` is set.
- Default header name is `x-api-key`; override via `VOICE_API_KEY_HEADER`.
- Omit the API key entirely for local unsecured usage (development only).

## Feature Files Example

Write test scenarios in natural, human-readable Gherkin syntax:

```gherkin
Feature: Voice Agent Billing Inquiry
  As a customer service system
  I want to handle billing inquiries properly
  So that customers can understand their charges

  Scenario: Customer inquires about bill increase
    Given a test case with id "billing_inquiry_v1"
    And the persona is "Calm Customer"
    And turn 1 where user says "Hi, I noticed my bill jumped this month."
    And the agent should respond with keywords "account, review, details"
    And turn 2 where user says "Can you explain the extra charges?"
    And the agent should respond with keywords "overage, usage, explain"
    When the test is executed
    Then the test should pass
    And 2 turns should be executed
```

**Benefits:**
- ✅ **Readable by non-developers** - Business stakeholders can write and review test scenarios
- ✅ **Self-documenting** - Feature files serve as living documentation
- ✅ **BDD approach** - Follows Behavior-Driven Development best practices  
- ✅ **Compatible with existing framework** - Integrates seamlessly with current test infrastructure
- ✅ **Tag support** - Run specific subsets of tests using `@smoke`, `@regression`, etc.

For more details, see:
- **Quick Start Guide**: [docs/QUICKSTART_FEATURES.md](docs/QUICKSTART_FEATURES.md)
- **Complete Reference**: [docs/FEATURE_FILES_GUIDE.md](docs/FEATURE_FILES_GUIDE.md)
- **Example Files**: `features/` directory

## Next Enhancements
- Wire real-time audio ingestion for Zoom Phone/SIP providers.
- Persist evaluator artifacts (audio URLs, embeddings) for richer analytics.
- Build LangChain agents that can automatically triage failures or generate new scripts from transcripts.
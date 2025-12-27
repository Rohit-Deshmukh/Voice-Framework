# Voice-Framework

Deterministic end-to-end testing harness for voice agents. The stack mirrors the original Next.js/Twilio workflow but runs entirely in Python (FastAPI + SQLModel) with optional LLM assist for simulator steering and evaluation.

## Features
- **Zero-configuration local mode** - Works out-of-the-box with in-memory storage, no database setup required
- **One-line setup** - Get running in seconds with automated setup scripts
- **Lightweight resource usage** - Optional LLM features and configurable memory limits for low-resource systems
- Modular layout (`core`, `api`, `models`, `services`, `scripts`) for clean separation of concerns.
- Telephony abstraction (`TelephonyProvider`) with a concrete Twilio implementation and placeholders for Zoom Phone / SIP trunks.
- Rich Pydantic models for scripted turn-by-turn expectations to enforce sequential logic.
- Simulator service that iterates through a `TestCase`, optionally naturalizing user prompts and steering on deviations via LLM.
- Evaluator service that performs zipper validation plus sentiment/QA scoring (LLM-backed when available).
- FastAPI endpoints for running simulations or live calls and processing provider webhooks.
- **Cucumber-style feature files** - Write test scenarios in natural language using Gherkin syntax for better readability and collaboration.

## ⚡ One-Line Setup

**Unix/Linux/macOS:**
```bash
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

**Using Make:**
```bash
make setup && make run
```

**Using Docker:**
```bash
docker-compose up
```

That's it! The API starts with sample test cases pre-loaded. See [Quick Setup Guide](docs/QUICK_SETUP.md) for details.

## Quick Start (Manual Installation)

If you prefer manual setup:

1. **Create a virtual environment**
	```bash
	python -m venv .venv
	source .venv/bin/activate  # On Windows: .venv\Scripts\activate
	```

2. **Install dependencies**
	```bash
	pip install -r requirements.txt
	```

3. **Run the API** (works immediately with in-memory storage!)
	```bash
	uvicorn api.main:app --reload
	```
	Sample test cases are automatically loaded on startup.

4. **Trigger a simulation**
	```bash
	curl -X POST http://localhost:8000/test/run \
	  -H "Content-Type: application/json" \
	  -d '{"test_id":"billing_inquiry_v1","provider":"twilio","mode":"simulation"}'
	```

---

**💡 Prefer even simpler setup?** Use `make setup && make run` or see [Quick Setup Guide](docs/QUICK_SETUP.md) for one-line installation options including Docker.

---

## Configuration Options

The framework works with sensible defaults but can be customized via environment variables:

### Storage Options

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_DATABASE` | `false` | Enable database storage (requires setup) |
| `DATABASE_URL` | `sqlite+aiosqlite:///./voice_framework.db` | SQLAlchemy connection string |

### Performance Optimization

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_LLM` | `false` | Enable LLM features (naturalization, steering, sentiment) |
| `MAX_TRANSCRIPT_SIZE` | `1000` | Maximum transcript entries per test run (prevents memory issues) |

### Optional API Keys (only needed if ENABLE_LLM=true)

```bash
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

### Twilio Integration (only for live calls)

```bash
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_DEFAULT_FROM=+15555555555
```

### API Authentication (optional)

```bash
VOICE_API_KEY=super-secret-token
VOICE_API_KEY_HEADER=x-api-key
```

## Advanced Setup (Optional Database Mode)

If you need persistent storage, enable database mode:

1. **Configure environment variables** (create a `.env` file)
	```bash
	USE_DATABASE=true
	DATABASE_URL=sqlite+aiosqlite:///./voice_framework.db
	```

2. **Seed test cases into database**
	```bash
	python scripts/seed_test_cases.py
	```

3. **Run the API**
	```bash
	uvicorn api.main:app --reload
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
- `scripts/seed_test_cases.py` &mdash; Inserts baseline deterministic scripts. Works with both in-memory and database storage based on `USE_DATABASE` setting.
- `scripts/run_features.py` &mdash; Executes Cucumber-style feature files using behave. Run with no arguments to execute all feature files.
- `scripts/load_features.py` &mdash; Parses feature files and loads them as test cases into storage (in-memory or database based on `USE_DATABASE`).
- `setup.sh` / `setup.bat` &mdash; Automated setup scripts for quick installation on any system.
- `Makefile` &mdash; Convenient shortcuts for common development tasks (`make setup`, `make run`, `make test`, etc.)

## Deployment Options

### Local Development
```bash
# Automated setup
./setup.sh              # Unix/Linux/macOS
setup.bat               # Windows

# Or use Make
make setup && make run

# Or manual
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### Docker
```bash
# Quick start with docker-compose
docker-compose up

# Or build and run manually
docker build -t voice-framework .
docker run -p 8000:8000 voice-framework
```

### CI/CD Integration
The framework is designed to work seamlessly in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Setup Voice Framework
  run: |
    pip install -r requirements.txt
    
- name: Run tests
  run: |
    uvicorn api.main:app &
    sleep 5
    pytest tests/
```

See [Quick Setup Guide](docs/QUICK_SETUP.md) for detailed deployment instructions.

## Streamlit Dashboard
Launch the reviewer console to orchestrate runs and inspect zipper outcomes:

```bash
VOICE_API_BASE_URL=http://localhost:8000 \
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

## Resource Usage & Performance

The framework is designed to run efficiently on systems with limited resources:

### Default Mode (Lightweight)
- **No database** - Uses in-memory storage (ephemeral)
- **No LLM calls** - Deterministic simulation only
- **Memory limits** - Configurable transcript size limits
- **Minimal dependencies** - Core functionality works without external services

### Resource Requirements
- **Minimum**: ~50MB RAM, works on any Python 3.8+ system
- **With LLM features**: Additional ~200MB RAM + API calls to OpenAI/Anthropic
- **With database**: Additional ~10MB RAM + disk space for SQLite

### Optimization Tips
1. **Keep `ENABLE_LLM=false`** for deterministic, fast testing without API costs
2. **Use in-memory storage** (`USE_DATABASE=false`) for ephemeral test runs
3. **Adjust `MAX_TRANSCRIPT_SIZE`** if testing very long conversations
4. **Run without Streamlit** for headless/CI environments to save resources

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
- **Quick Setup**: [docs/QUICK_SETUP.md](docs/QUICK_SETUP.md) - One-line installation guide
- **Quick Start Guide**: [docs/QUICKSTART_FEATURES.md](docs/QUICKSTART_FEATURES.md)
- **Complete Reference**: [docs/FEATURE_FILES_GUIDE.md](docs/FEATURE_FILES_GUIDE.md)
- **Call Direction Guide**: [docs/CALL_DIRECTION_GUIDE.md](docs/CALL_DIRECTION_GUIDE.md) - Phone number configuration
- **Performance Optimization**: [docs/PERFORMANCE_OPTIMIZATION.md](docs/PERFORMANCE_OPTIMIZATION.md)
- **Example Files**: `features/` directory

## Next Enhancements
- Wire real-time audio ingestion for Zoom Phone/SIP providers.
- Persist evaluator artifacts (audio URLs, embeddings) for richer analytics.
- Build LangChain agents that can automatically triage failures or generate new scripts from transcripts.
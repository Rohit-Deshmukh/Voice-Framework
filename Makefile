# Voice Framework - Makefile for common tasks
# Makes development and setup even easier

.PHONY: help setup install run test clean lint format docker-build docker-run

# Default target
help:
	@echo "Voice Framework - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Complete setup (venv + install dependencies)"
	@echo "  make install        - Install dependencies only"
	@echo "  make install-dev    - Install with development dependencies"
	@echo ""
	@echo "Running:"
	@echo "  make run            - Start the API server"
	@echo "  make dashboard      - Start the Streamlit dashboard"
	@echo "  make demo           - Run a demo test"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-features  - Run feature file tests"
	@echo ""
	@echo "Development:"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make clean          - Clean build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run in Docker container"
	@echo ""

# Setup everything
setup:
	@echo "Setting up Voice Framework..."
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv .venv; \
	fi
	@echo "Installing dependencies..."
	@. .venv/bin/activate && pip install --upgrade pip -q && pip install -r requirements.txt -q
	@if [ ! -f ".env" ] && [ -f ".env.example" ]; then \
		cp .env.example .env; \
		echo ".env file created from template"; \
	fi
	@echo ""
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Next: Run 'make run' to start the API server"

# Install dependencies only
install:
	@. .venv/bin/activate && pip install -r requirements.txt

# Install with dev dependencies
install-dev:
	@. .venv/bin/activate && pip install -r requirements.txt -r requirements-features.txt

# Run the API server
run:
	@echo "Starting Voice Framework API..."
	@. .venv/bin/activate && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Run the Streamlit dashboard
dashboard:
	@echo "Starting Streamlit dashboard..."
	@. .venv/bin/activate && streamlit run streamlit_app.py

# Run a demo test
demo:
	@echo "Running demo test..."
	@sleep 2
	@curl -X POST http://localhost:8000/test/run \
		-H "Content-Type: application/json" \
		-d '{"test_id":"billing_inquiry_v1","provider":"twilio","mode":"simulation"}' \
		| python -m json.tool

# Run tests
test:
	@echo "Running tests..."
	@. .venv/bin/activate && pytest tests/ -v

# Run feature file tests
test-features:
	@echo "Running feature file tests..."
	@. .venv/bin/activate && python scripts/run_features.py

# Lint code
lint:
	@echo "Running linters..."
	@. .venv/bin/activate && \
		if command -v ruff >/dev/null 2>&1; then \
			ruff check .; \
		else \
			echo "Ruff not installed. Install with: pip install ruff"; \
		fi

# Format code
format:
	@echo "Formatting code..."
	@. .venv/bin/activate && \
		if command -v ruff >/dev/null 2>&1; then \
			ruff format .; \
		else \
			echo "Ruff not installed. Install with: pip install ruff"; \
		fi

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf __pycache__ .pytest_cache .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".DS_Store" -delete
	@rm -f voice_framework.db
	@echo "✓ Cleaned"

# Docker build
docker-build:
	@echo "Building Docker image..."
	@docker build -t voice-framework:latest .

# Docker run
docker-run:
	@echo "Running in Docker..."
	@docker run -p 8000:8000 voice-framework:latest

# Quick start (setup + run)
start: setup run

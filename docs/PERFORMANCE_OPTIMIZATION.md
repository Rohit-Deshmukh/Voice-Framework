# Performance Optimization Guide

This guide explains how to configure the Voice Framework for optimal performance based on your system resources and requirements.

## Overview

The Voice Framework is designed to work efficiently on systems with limited resources. By default, it uses **in-memory storage** and **deterministic testing** without requiring any external services.

## Configuration Modes

### 1. Minimal Mode (Default) - Best for CI/CD and Low-Resource Systems

**Resource Requirements**: ~50MB RAM, no external dependencies

```bash
# No configuration needed - just run!
uvicorn api.main:app
```

**Features**:
- ✅ In-memory storage (no database setup)
- ✅ Deterministic simulation (no LLM API calls)
- ✅ Auto-loaded sample test cases
- ✅ Fast startup (<1 second)
- ✅ No external service dependencies

**Use Cases**:
- CI/CD pipelines
- Development machines with limited resources
- Quick testing and prototyping
- Docker containers with minimal memory

### 2. Enhanced Mode - With LLM Features

**Resource Requirements**: ~250MB RAM + API access to OpenAI/Anthropic

```bash
# .env file
ENABLE_LLM=true
OPENAI_API_KEY=your_api_key_here
# OR
ANTHROPIC_API_KEY=your_api_key_here
```

**Additional Features**:
- Natural language variation in user prompts
- Intelligent steering when agent deviates
- LLM-powered sentiment analysis
- More realistic conversation simulation

**Trade-offs**:
- Slower execution (~2-5 seconds per test due to API calls)
- Costs associated with LLM API usage
- Requires internet connectivity
- Non-deterministic results

### 3. Persistent Mode - With Database

**Resource Requirements**: ~60MB RAM + disk space

```bash
# .env file
USE_DATABASE=true
DATABASE_URL=sqlite+aiosqlite:///./voice_framework.db
```

**Additional Features**:
- Persistent test case storage
- Historical test run data
- Survives application restarts

**Trade-offs**:
- Slightly slower startup (database initialization)
- Requires running seed script initially
- Additional disk I/O overhead

### 4. Full Mode - All Features Enabled

**Resource Requirements**: ~300MB RAM + disk space + API access

```bash
# .env file
USE_DATABASE=true
ENABLE_LLM=true
DATABASE_URL=sqlite+aiosqlite:///./voice_framework.db
OPENAI_API_KEY=your_api_key_here
```

## Memory Optimization

### Transcript Size Limiting

For long-running test sessions or systems with limited RAM:

```bash
# .env file
MAX_TRANSCRIPT_SIZE=500  # Default is 1000
```

This limits the number of transcript entries kept in memory per test run. Older entries are automatically trimmed.

**Recommendations**:
- **Very low memory** (<256MB available): `MAX_TRANSCRIPT_SIZE=100`
- **Normal usage**: `MAX_TRANSCRIPT_SIZE=1000` (default)
- **High-volume testing**: `MAX_TRANSCRIPT_SIZE=5000`

## Performance Benchmarks

### Startup Time

| Mode | Time | Notes |
|------|------|-------|
| Minimal (in-memory, no LLM) | ~0.5s | Fastest |
| With database | ~1.5s | Database initialization |
| With LLM enabled | ~0.6s | LLM client setup |
| Full mode | ~1.6s | All features |

### Test Execution Time (per test case with 3 turns)

| Mode | Time | Notes |
|------|------|-------|
| Deterministic | ~0.01s | Instant, in-memory |
| With LLM naturalization | ~3-5s | API latency |
| Live mode (Twilio) | ~30-60s | Real telephony |

### Memory Usage

| Mode | RAM | Notes |
|------|-----|-------|
| Minimal | ~50MB | Core framework only |
| With database | ~60MB | SQLite overhead |
| With LLM | ~250MB | OpenAI/Anthropic clients |
| Full mode | ~300MB | All features loaded |

## Optimization Tips

### 1. For CI/CD Pipelines

```bash
# Use defaults - fastest and most reliable
uvicorn api.main:app
```

**Benefits**:
- Fast execution
- No external dependencies
- Deterministic results
- Easy to containerize

### 2. For Development

```bash
# .env
USE_DATABASE=false  # Quick iterations
ENABLE_LLM=false    # Fast feedback
```

Run tests frequently without waiting for LLM APIs or database writes.

### 3. For Production-Like Testing

```bash
# .env
USE_DATABASE=true   # Persistent storage
ENABLE_LLM=true     # Realistic simulation
MAX_TRANSCRIPT_SIZE=2000  # Handle longer conversations
```

### 4. For Resource-Constrained Environments

```bash
# .env
USE_DATABASE=false  # No disk I/O
ENABLE_LLM=false    # No API calls
MAX_TRANSCRIPT_SIZE=100  # Minimal memory
```

Example: Raspberry Pi, Docker with 256MB limit, or serverless functions.

## Containerization

### Minimal Docker Image

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# No environment variables needed - uses defaults
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Image size**: ~150MB  
**Memory limit**: 128MB minimum

### With Database

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV USE_DATABASE=true
ENV DATABASE_URL=sqlite+aiosqlite:////data/voice_framework.db

VOLUME ["/data"]

CMD ["sh", "-c", "python scripts/seed_test_cases.py && uvicorn api.main:app --host 0.0.0.0 --port 8000"]
```

## Troubleshooting

### High Memory Usage

**Problem**: Application using more memory than expected

**Solutions**:
1. Reduce `MAX_TRANSCRIPT_SIZE`
2. Disable LLM features (`ENABLE_LLM=false`)
3. Use in-memory storage (`USE_DATABASE=false`)
4. Restart periodically to clear accumulated data

### Slow Test Execution

**Problem**: Tests taking too long to run

**Solutions**:
1. Disable LLM features (`ENABLE_LLM=false`) for deterministic mode
2. Use in-memory storage (`USE_DATABASE=false`)
3. Check network latency if using LLM APIs
4. Consider batching test executions

### Out of Memory Errors

**Problem**: Application crashes with OOM errors

**Solutions**:
1. Set `MAX_TRANSCRIPT_SIZE=100` or lower
2. Ensure `USE_DATABASE=false` for ephemeral storage
3. Ensure `ENABLE_LLM=false` to reduce memory overhead
4. Increase container/system memory if possible

## Monitoring

### Check Current Resource Usage

```bash
# Monitor memory usage
ps aux | grep uvicorn

# Monitor with top
top -p $(pgrep -f uvicorn)

# Docker stats
docker stats <container_name>
```

### Log Startup Configuration

The framework logs its configuration on startup. Look for:
```
✓ Auto-loaded 2 sample test cases to in-memory storage.
```

This confirms in-memory mode is active.

## Best Practices

1. **Start with defaults** - The minimal mode works for 90% of use cases
2. **Add features incrementally** - Enable database or LLM only when needed
3. **Monitor resource usage** - Check memory consumption in production
4. **Use appropriate limits** - Set `MAX_TRANSCRIPT_SIZE` based on your use case
5. **Profile before optimizing** - Measure actual resource usage before making changes

## Summary

| Use Case | USE_DATABASE | ENABLE_LLM | MAX_TRANSCRIPT_SIZE | RAM |
|----------|--------------|------------|---------------------|-----|
| CI/CD | `false` | `false` | 100-500 | 50MB |
| Development | `false` | `false` | 1000 | 50MB |
| Testing with realism | `false` | `true` | 1000 | 250MB |
| Production | `true` | `true` | 2000+ | 300MB |
| Low-resource | `false` | `false` | 100 | 50MB |

Choose the configuration that best matches your requirements and available resources.

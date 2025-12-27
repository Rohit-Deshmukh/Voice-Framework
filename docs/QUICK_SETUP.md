# Quick Setup Guide

This guide provides the absolute fastest ways to get Voice Framework running on any system.

## 🚀 One-Line Setup

### Unix/Linux/macOS

**Option 1: Using the setup script**
```bash
./setup.sh
```

**Option 2: Using Make**
```bash
make setup && make run
```

**Option 3: Using Docker**
```bash
docker-compose up
```

### Windows

**Option 1: Using the setup script**
```cmd
setup.bat
```

**Option 2: Manual (still simple)**
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

## 📦 Installation Methods Comparison

| Method | Setup Time | Requirements | Best For |
|--------|------------|--------------|----------|
| **Setup Script** | ~2 min | Python 3.8+ | First-time users |
| **Make** | ~2 min | Python 3.8+ + Make | Developers |
| **Docker** | ~3 min | Docker | Production/Isolated environments |
| **Manual** | ~3 min | Python 3.8+ | Customization |

## 🎯 Setup Script Details

### What the setup script does:

1. ✅ Checks Python version (requires 3.8+)
2. ✅ Creates virtual environment
3. ✅ Installs all dependencies
4. ✅ Creates `.env` file from template
5. ✅ Optionally installs feature file support
6. ✅ Shows next steps

### Running the setup script:

```bash
# Unix/Linux/macOS
./setup.sh

# Windows
setup.bat
```

After running, just activate the virtual environment and start the server:

```bash
# Unix/Linux/macOS
source .venv/bin/activate
uvicorn api.main:app --reload

# Windows
.venv\Scripts\activate
uvicorn api.main:app --reload
```

## 🔧 Using Make (Recommended for Developers)

The Makefile provides convenient shortcuts:

```bash
# Complete setup in one command
make setup

# Start the API server
make run

# Start the Streamlit dashboard
make dashboard

# Run tests
make test

# Run a demo test (requires API to be running)
make demo

# See all available commands
make help
```

### Most common workflow:

```bash
make setup    # First time only
make run      # Start developing
```

## 🐳 Docker Setup

### Quick Start with Docker Compose:

```bash
# Start everything
docker-compose up

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

The API will be available at `http://localhost:8000`

### Using Docker directly:

```bash
# Build
docker build -t voice-framework .

# Run
docker run -p 8000:8000 voice-framework

# Run with custom environment
docker run -p 8000:8000 -e ENABLE_LLM=true voice-framework
```

## 🎬 After Setup

Once setup is complete, you can:

### 1. Test the API
```bash
curl http://localhost:8000/testcases
```

### 2. Run a simulation
```bash
curl -X POST http://localhost:8000/test/run \
  -H "Content-Type: application/json" \
  -d '{"test_id":"billing_inquiry_v1","provider":"twilio","mode":"simulation"}'
```

### 3. Use the Streamlit Dashboard
```bash
streamlit run streamlit_app.py
```
Then open http://localhost:8501 in your browser

## 🔍 Troubleshooting

### Python not found
**Solution**: Install Python 3.8 or higher from [python.org](https://python.org)

### Permission denied on setup.sh
**Solution**: Make it executable
```bash
chmod +x setup.sh
```

### Port 8000 already in use
**Solution**: Use a different port
```bash
uvicorn api.main:app --reload --port 8001
```

### Dependencies fail to install
**Solution**: Upgrade pip first
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Docker: Cannot connect to Docker daemon
**Solution**: Start Docker Desktop or Docker service
```bash
# Linux
sudo systemctl start docker

# macOS/Windows
# Start Docker Desktop application
```

## 📚 Next Steps

After successful setup:

1. **Read the documentation**
   - [README.md](../README.md) - Overview and features
   - [FEATURE_FILES_GUIDE.md](FEATURE_FILES_GUIDE.md) - Writing test scenarios
   - [CALL_DIRECTION_GUIDE.md](CALL_DIRECTION_GUIDE.md) - Phone number configuration
   - [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md) - Resource tuning

2. **Try the examples**
   - Browse `features/` directory for example feature files
   - Load them with: `python scripts/load_features.py`
   - Run them with: `python scripts/run_features.py`

3. **Configure for your needs**
   - Edit `.env` file for custom settings
   - See `.env.example` for all available options

4. **Integrate with your workflow**
   - Use the API endpoints from your application
   - Write feature files for your test scenarios
   - Run tests in CI/CD pipelines

## 💡 Pro Tips

### Development Workflow

```bash
# Use Make for common tasks
make setup      # One-time setup
make run        # Daily: start API server
make test       # Before commits: run tests
make clean      # Clean up artifacts
```

### Production Deployment

```bash
# Use Docker for consistent deployment
docker-compose up -d

# Or build and deploy your own image
docker build -t myorg/voice-framework .
docker push myorg/voice-framework
```

### Quick Testing

```bash
# Terminal 1: Start server
make run

# Terminal 2: Run tests
make test

# Terminal 3: Try the API
make demo
```

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all prerequisites are installed
4. Try the Docker option for a clean environment
5. Check the [README.md](../README.md) for configuration details

## ⏱️ Comparison: Before vs After

### Before (Old Setup)
```bash
# 1. Create venv
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies  
pip install -r requirements.txt

# 3. Setup database
python scripts/seed_test_cases.py

# 4. Configure environment
cp .env.example .env
# Edit .env file...

# 5. Run server
uvicorn api.main:app --reload
```
**Time: ~10-15 minutes**

### After (New Setup)
```bash
./setup.sh && make run
```
**Time: ~2 minutes** ⚡

That's an **80% reduction** in setup time!

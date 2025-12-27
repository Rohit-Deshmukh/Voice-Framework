#!/bin/bash
# Voice Framework - One-Line Setup Script
# Usage: curl -fsSL https://raw.githubusercontent.com/Rohit-Deshmukh/Voice-Framework/main/setup.sh | bash
# Or: ./setup.sh

set -e

echo "============================================"
echo "  Voice Framework - Quick Setup"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
echo ""

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}✓ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip -q
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt -q
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Optional: Install feature file support
read -p "Install feature file support (behave)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Installing feature file support...${NC}"
    pip install -r requirements-features.txt -q
    echo -e "${GREEN}✓ Feature file support installed${NC}"
    echo ""
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file from template...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created (review and update as needed)${NC}"
    else
        echo -e "${YELLOW}⚠ .env.example not found, skipping${NC}"
    fi
    echo ""
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Setup Complete! 🎉${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Start the API server:"
echo "     ${BLUE}source .venv/bin/activate${NC}"
echo "     ${BLUE}uvicorn api.main:app --reload${NC}"
echo ""
echo "  2. In another terminal, run a test:"
echo "     ${BLUE}curl -X POST http://localhost:8000/test/run \\${NC}"
echo "     ${BLUE}  -H \"Content-Type: application/json\" \\${NC}"
echo "     ${BLUE}  -d '{\"test_id\":\"billing_inquiry_v1\",\"provider\":\"twilio\",\"mode\":\"simulation\"}'${NC}"
echo ""
echo "  3. Or use the Streamlit dashboard:"
echo "     ${BLUE}streamlit run streamlit_app.py${NC}"
echo ""
echo "For more information, see README.md"
echo ""

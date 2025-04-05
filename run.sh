#!/bin/bash

# DeepCAL++ System Launcher
# This script sets up the environment and launches the DeepCAL++ system

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}      DeepCAL++ System Launcher       ${NC}"
echo -e "${BLUE}=======================================${NC}"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install requirements
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo -e "${YELLOW}Installing Streamlit...${NC}"
    pip install streamlit
fi

# Launch the application
echo -e "${GREEN}Launching DeepCAL++ System...${NC}"
streamlit run frontend/app.py


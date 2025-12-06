#!/bin/bash
echo "Starting Agentic Travel Planner Backend..."
cd "$(dirname "$0")"
source .venv/Scripts/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

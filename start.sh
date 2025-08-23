#!/bin/bash
set -e

echo "Initializing DB..."
python scripts/init_db.py
python scripts/load_data.py

echo "Starting FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT

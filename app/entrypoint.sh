#!/bin/bash
set -e

# Print startup message
echo "Starting Time Tracker services..."

# Start Streamlit app in background
echo "Starting Streamlit UI on port 8501..."
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 &
STREAMLIT_PID=$!

# Start FastAPI webhook server in background
echo "Starting FastAPI webhook server on port 8000..."
python -m uvicorn webhook_server:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# Function to handle shutdown
function cleanup() {
    echo "Shutting down services..."
    kill -TERM $STREAMLIT_PID
    kill -TERM $FASTAPI_PID
    wait $STREAMLIT_PID
    wait $FASTAPI_PID
    echo "All services terminated."
    exit 0
}

# Trap SIGTERM and SIGINT signals
trap cleanup SIGTERM SIGINT

# Monitor child processes
echo "Services started successfully!"
echo "Streamlit PID: $STREAMLIT_PID"
echo "FastAPI PID: $FASTAPI_PID"

# Wait for any process to exit
wait -n

# If we get here, one of the processes exited, so we should exit too
echo "One of the services exited! Shutting down..."
cleanup
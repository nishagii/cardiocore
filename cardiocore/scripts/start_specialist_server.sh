#!/bin/bash
# Binula runs this on Instance B (Ubuntu AMD cloud)
# Starts the specialist model server on Port 9001

cd "/.."
echo "Starting CardioCore specialist server on Port 9001..."
uvicorn specialist_server.main:app \
    --host 0.0.0.0 \
    --port 9001 \
    --reload \
    --log-level info

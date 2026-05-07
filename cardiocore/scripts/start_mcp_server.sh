#!/bin/bash
# Binula runs this on Instance B (Ubuntu AMD cloud)
# Starts the MCP server on Port 8000

cd "/.."
echo "Starting CardioCore MCP server on Port 8000..."
uvicorn mcp_server.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info

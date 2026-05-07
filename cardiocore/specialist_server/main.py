# OWNER: Binula
# DAY:   2
# PURPOSE: FastAPI server (Port 9001) on Instance B
#          Loads all three specialist models and exposes them as HTTP endpoints
#          Called by Teammate A's MCP tools (Tools 1, 2, 3)
#
# Endpoints:
#   GET  /health                  â€” check all models are loaded
#   POST /models/ecg/classify     â€” ECG image -> rhythm classification dict
#   POST /models/echo/ef          â€” echo video -> EF estimation dict
#   POST /models/echo/structure   â€” echo video -> structural analysis dict
#
# Start this on Instance B with:
#   uvicorn specialist_server.main:app --host 0.0.0.0 --port 9001
#
# Share Instance B IP with Teammate A so they can configure their .env

# TODO: Binula implements this on Day 2
# See implementation guide for full code

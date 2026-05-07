# OWNER: Teammate A
# DAY:   3
# PURPOSE: Main FastAPI MCP server â€” wires all 5 tool routers
#          Runs on Port 8000 on Instance B
#
# Endpoints served:
#   POST /tools/analyze_ecg_leads
#   POST /tools/estimate_ejection_fraction
#   POST /tools/analyze_cardiac_structure
#   POST /tools/risk_stratify
#   POST /tools/generate_cardiac_report
#   GET  /health
#   GET  /mcp/tools        <- Prompt Opinion reads this to discover tools
#   GET  /.well-known/mcp  <- MCP discovery endpoint
#
# Start with:
#   uvicorn mcp_server.main:app --host 0.0.0.0 --port 8000

# TODO: Teammate A implements this on Day 3
# See implementation guide for full code

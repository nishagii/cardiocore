#!/bin/bash
# Run on Instance B to check all services are working
# Usage: bash scripts/health_check.sh

echo ""
echo "=== CardioCore Health Check ==="
echo ""

echo "1. GPU status:"
rocm-smi 2>/dev/null | head -5 || echo "   rocm-smi not available"

echo ""
echo "2. vLLM / Gemma 4 (http://localhost:9000):"
curl -s http://localhost:9000/v1/models 2>/dev/null | python3 -m json.tool 2>/dev/null \
    || echo "   NOT REACHABLE â€” run: bash scripts/start_vllm.sh"

echo ""
echo "3. Specialist server (http://localhost:9001):"
curl -s http://localhost:9001/health 2>/dev/null | python3 -m json.tool 2>/dev/null \
    || echo "   NOT REACHABLE â€” run: bash scripts/start_specialist_server.sh"

echo ""
echo "4. MCP server (http://localhost:8000):"
curl -s http://localhost:8000/health 2>/dev/null | python3 -m json.tool 2>/dev/null \
    || echo "   NOT REACHABLE â€” run: bash scripts/start_mcp_server.sh"

echo ""
echo "5. MCP tools manifest:"
curl -s http://localhost:8000/mcp/tools 2>/dev/null \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('   Tools:', [t['name'] for t in d.get('tools',[])])" 2>/dev/null \
    || echo "   MCP server not reachable"
echo ""

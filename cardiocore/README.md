# CardioCore

Agentic cardiac assessment MCP suite on AMD MI300X.

## Five MCP Tools

| Tool | Input | Output |
|------|-------|--------|
| analyze_ecg_leads | ECG image (PNG/JPEG) | Rhythm class + SNOMED + FHIR Observation |
| estimate_ejection_fraction | Echo video (AVI/MP4) | EF% + HF classification + FHIR Observation |
| analyze_cardiac_structure | Echo video (AVI/MP4) | Wall thickness + chamber flags |
| risk_stratify | ECG + Echo + clinical context | HEART score + Urgent/Routine/Normal |
| generate_cardiac_report | All above | FHIR R4 DiagnosticReport bundle |

## Architecture

Two AMD MI300X instances:
- Instance A (Teammate A): Gemma 4 12B via vLLM â€” clinical reasoning + FHIR generation
- Instance B (Binula): ECG classifier + EchoNet + EchoFM + FastAPI MCP server

## Datasets

- PTB-XL: physionet.org/content/ptb-xl (21,799 ECGs, 88% accuracy)
- EchoNet-Dynamic: echonet.github.io/dynamic (10,030 echo videos, MAE ~4%)
- EchoFM: github.com/SekeunKim/EchoFM (20M+ echo images)

## Quickstart

cp .env.example .env
# Edit .env with your HF_TOKEN and instance IPs

# Instance B: start specialist server
uvicorn specialist_server.main:app --host 0.0.0.0 --port 9001

# Instance B: start MCP server
uvicorn mcp_server.main:app --host 0.0.0.0 --port 8000

# Test
curl http://localhost:8000/health
curl http://localhost:8000/mcp/tools

## Hackathons

- AMD Developer Hackathon: Track 1 + Track 3 + Build in Public
- Agents Assemble Healthcare: Option 1 MCP + Option 2 A2A

## License

Apache-2.0

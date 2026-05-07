# CardioCore â€” Technical Write-up
# OWNER: Binula | DAY: 5
# Fill in all TODO sections using actual numbers from latency_results.json

## Problem

20+ million people have undiagnosed arrhythmias. Interpreting ECGs and
echocardiograms is bottlenecked by cardiologist availability, especially
in rural and low-resource settings.

## Solution

CardioCore is a distributed agentic cardiac assessment system on two AMD
MI300X instances. Five MCP tools give any clinical agent the ability to
analyse heart data and produce a validated FHIR DiagnosticReport in under
five seconds.

## Architecture

Two AMD MI300X instances:
- Instance A (Teammate A): Gemma 4 12B via vLLM â€” clinical reasoning
- Instance B (Binula): ECG classifier + EchoNet + EchoFM + MCP server

Request flow:
1. Clinical agent uploads ECG image -> analyze_ecg_leads
2. Clinical agent uploads echo video -> estimate_ejection_fraction + analyze_cardiac_structure
3. Combined results -> risk_stratify (HEART score)
4. All results -> generate_cardiac_report (FHIR bundle)

## Datasets

| Dataset | Source | Records | Published Accuracy | Used For |
|---------|--------|---------|-------------------|----------|
| PTB-XL | physionet.org/content/ptb-xl | 21,799 ECGs | 88% (test set) | ECG classifier |
| EchoNet-Dynamic | echonet.github.io/dynamic | 10,030 videos | MAE ~4% | EF estimation |
| EchoFM | github.com/SekeunKim/EchoFM | 20M+ images | - | Structural analysis |

## Models

- ECG Classifier: HuggingFace Syed-Mujtaba-Hassan/ECG-Classification (PTB-XL trained)
- EchoNet: Stanford pretrained R(2+1)D model (echonet.github.io/dynamic)
- EchoFM: Foundation model for echocardiography (CC-BY-NC-ND 4.0)
- Gemma 4 12B-IT: Google, served via vLLM ROCm on AMD MI300X

## Benchmark Results

TODO: Paste from benchmarks/latency_results.json after Day 4

Example format:
| Concurrency | Mean (ms) | P95 (ms) | Throughput/s |
|-------------|-----------|----------|--------------|
| 1 | X | X | X |
| 2 | X | X | X |
| 4 | X | X | X |

## FHIR Output Example

TODO: Paste DiagnosticReport.conclusion from demo/output/fhir_bundle.json after Day 4

## AMD Hackathon Tracks

- Track 1 (AI Agents): Five-tool agentic pipeline on AMD cloud
- Track 3 (Vision & Multimodal): ECG images + echo video on AMD MI300X
- Build in Public: Social posts + ROCm feedback + open source repo

## Healthcare Hackathon

- Option 1 (MCP Superpower): All 5 tools on Prompt Opinion marketplace
- Option 2 (A2A Agent): Cardiology Triage Agent (no-code, 5-step workflow)

## How to Run

cp .env.example .env
# Edit .env with HF_TOKEN and instance IPs

# Instance B: start specialist server
uvicorn specialist_server.main:app --host 0.0.0.0 --port 9001

# Instance B: start MCP server
uvicorn mcp_server.main:app --host 0.0.0.0 --port 8000

# Verify
curl http://localhost:8000/health
curl http://localhost:8000/mcp/tools

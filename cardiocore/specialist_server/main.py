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

import torch
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile, time
from pathlib import Path

_ecg = None

@asynccontextmanager
async def lifespan(app):
    global _ecg
    print('Loading ECG classifier...')
    from transformers import pipeline
    _ecg = pipeline('image-classification',
                    model='Syed-Mujtaba-Hassan/ECG-Classification', device=0)
    print(f'ECG ready. GPU: {torch.cuda.memory_allocated()/1e9:.2f}GB')
    # EchoNet loaded separately in inference/echonet_loader.py when available
    # EchoFM loaded separately in inference/echo_structure.py
    print('Specialist server ready.')
    yield

app = FastAPI(title='CardioCore Specialist Server', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['*'],
                   allow_methods=['*'], allow_headers=['*'])

@app.get('/health')
def health():
    return {'status':'healthy','ecg_loaded':_ecg is not None,
            'gpu_gb':round(torch.cuda.memory_allocated()/1e9,2)}

@app.post('/models/ecg/classify')
async def classify_ecg(file: UploadFile = File(...)):
    content = await file.read()
    from inference.ecg import analyze_from_image_bytes
    return analyze_from_image_bytes(content)

@app.post('/models/echo/ef')
async def estimate_ef(file: UploadFile = File(...)):
    content = await file.read()
    ext = Path(file.filename or 'echo.avi').suffix
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as t:
        t.write(content); tmp = t.name
    from inference.echo import analyze_echo
    result = analyze_echo(tmp)
    Path(tmp).unlink(missing_ok=True)
    return result

@app.post('/models/echo/structure')
async def analyze_structure(file: UploadFile = File(...)):
    content = await file.read()
    ext = Path(file.filename or 'echo.avi').suffix
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as t:
        t.write(content); tmp = t.name
    from inference.echo_structure import analyze_structure
    result = analyze_structure(tmp)
    Path(tmp).unlink(missing_ok=True)
    return result



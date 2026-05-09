import torch
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from pathlib import Path

_pulse_loaded = False

@asynccontextmanager
async def lifespan(app):
    global _pulse_loaded

    print('========== STARTING PULSE LOAD ==========')

    from inference.ecg_pulse import _load_model

    print('IMPORT SUCCESS')

    model, processor = _load_model()

    print('MODEL LOAD SUCCESS')

    _pulse_loaded = True

    print(
        f'PULSE-7B ready. GPU: '
        f'{torch.cuda.memory_allocated()/1e9:.2f}GB'
    )

    print('Specialist server ready.')

    yield


app = FastAPI(title='CardioCore Specialist Server', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['*'],
                   allow_methods=['*'], allow_headers=['*'])


@app.get('/health')
def health():
    return {
        'status': 'healthy',
        'pulse_loaded': _pulse_loaded,
        'gpu_gb': round(torch.cuda.memory_allocated()/1e9, 2)
                  if torch.cuda.is_available() else 0,
    }


@app.post('/models/ecg/classify')
async def classify_ecg(file: UploadFile = File(...)):
    content = await file.read()
    from inference.ecg_pulse import analyze_ecg_image
    return analyze_ecg_image(content)


@app.post('/models/echo/ef')
async def estimate_ef(file: UploadFile = File(...)):
    content = await file.read()
    ext = Path(file.filename or 'echo.avi').suffix
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as t:
        t.write(content)
        tmp = t.name
    try:
        from inference.echo import analyze_echo
        result = analyze_echo(tmp)
    finally:
        Path(tmp).unlink(missing_ok=True)
    return result


@app.post('/models/echo/structure')
async def echo_structure_endpoint(file: UploadFile = File(...)):
    content = await file.read()
    ext = Path(file.filename or 'echo.avi').suffix
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as t:
        t.write(content)
        tmp = t.name
    try:
        from inference.echo_structure import analyze_structure
        result = analyze_structure(tmp)
    finally:
        Path(tmp).unlink(missing_ok=True)
    return result
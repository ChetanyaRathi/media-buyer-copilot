from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import agent, ingest
from .config import get_settings
from .graph import run_pipeline
from .schema import AnalysisResult, ChatRequest, ChatResponse

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"

app = FastAPI(title="media-buyer-copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _rows_from_file(content: bytes, filename: str) -> list[dict]:
    df = ingest.load_dataframe(content, filename)
    if df.empty:
        raise ValueError(f"'{filename}' has no rows.")
    platform = ingest.detect_platform(filename, df.columns)
    mapping = ingest.map_columns(df, platform)
    return ingest.to_canonical(df, mapping, platform)


@app.get("/health")
def health():
    settings = get_settings()
    return {"status": "ok", "provider": settings.provider, "model": settings.model, "llm_configured": settings.llm_enabled}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze(files: list[UploadFile] = File(...)):
    rows: list[dict] = []
    errors: list[str] = []
    for upload in files:
        try:
            content = await upload.read()
            rows.extend(_rows_from_file(content, upload.filename))
        except ValueError as error:
            errors.append(str(error))
    if not rows:
        raise HTTPException(status_code=400, detail=" ".join(errors) or "No usable rows found in the upload.")
    return run_pipeline(rows)


@app.post("/analyze/sample", response_model=AnalysisResult)
def analyze_sample():
    rows: list[dict] = []
    for path in sorted(SAMPLE_DIR.glob("*.csv")):
        rows.extend(_rows_from_file(path.read_bytes(), path.name))
    if not rows:
        raise HTTPException(status_code=500, detail="Sample data not found.")
    return run_pipeline(rows)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return {"answer": agent.chat(request.question, request.context)}

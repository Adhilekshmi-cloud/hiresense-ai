"""
FastAPI REST API for the AI Resume Screening System.

Endpoints
---------
POST /api/upload-resume     Upload a resume (PDF/DOCX/TXT)
POST /api/screen            Screen uploaded resumes against a job description
POST /api/compare-models    Compare TF-IDF vs Transformer models
GET  /api/resumes           List uploaded resumes
DELETE /api/resumes         Clear all uploaded resumes
"""
from __future__ import annotations

import sys
import logging
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Ensure project root is on sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

_frontend_dir = _project_root / "frontend"

from app.config import settings
from app.models import (
    ScreenRequest,
    ScreenResponse,
    CandidateResult,
    ScoreBreakdown,
    UploadResponse,
    CompareModelsRequest,
    CompareModelsResponse,
    ModelBenchmarkResponse,
)
from core.pipeline import parse_resume, ParseError
from core.text_cleaner import process_resume, ResumeData
from core.embeddings import EmbeddingManager
from core.scoring import ResumeScorer
from core.explainer import ResumeExplainer
from core.evaluator import ModelEvaluator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── App factory ────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Resume Screening API",
    description=(
        "Production-grade resume screening system with semantic similarity, "
        "weighted scoring, explainability, and model comparison."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory store ───────────────────────────────────────────────────────

_resume_store: dict[str, ResumeData] = {}  # filename → processed data


# ── Endpoints ──────────────────────────────────────────────────────────────


@app.get("/", tags=["Health"])
async def root():
    """Serve the web app frontend."""
    index_file = _frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "status": "healthy",
        "service": "AI Resume Screening API",
        "version": "2.0.0",
        "resumes_loaded": len(_resume_store),
        "web_app": "frontend/index.html not found",
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Resume Screening API",
        "version": "2.0.0",
        "resumes_loaded": len(_resume_store),
    }


# Mount static files for CSS/JS assets (MUST be after route definitions)
if _frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend_dir)), name="static")


@app.post(
    "/api/upload-resume",
    response_model=UploadResponse,
    tags=["Resumes"],
    summary="Upload a single resume file",
)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume in PDF, DOCX, or TXT format.
    The file is parsed, cleaned, and stored in memory for screening.
    """
    # Validate extension
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()
    if ext not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Accepted: .pdf, .docx, .txt",
        )

    content = await file.read()

    # Validate size
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {settings.MAX_FILE_SIZE_MB} MB limit.",
        )

    # Parse
    try:
        raw_text = parse_resume(content, filename=filename)
    except ParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Process
    resume_data = process_resume(raw_text, filename=filename)
    _resume_store[filename] = resume_data

    return UploadResponse(
        message=f"'{filename}' uploaded and processed successfully.",
        filename=filename,
        skills_found=resume_data.skills,
        experience_years=resume_data.experience_years,
        education=resume_data.education,
    )


@app.get("/api/resumes", tags=["Resumes"], summary="List uploaded resumes")
async def list_resumes():
    return {
        "count": len(_resume_store),
        "resumes": [
            {
                "filename": rd.filename,
                "skills": rd.skills,
                "experience_years": rd.experience_years,
            }
            for rd in _resume_store.values()
        ],
    }


@app.delete("/api/resumes", tags=["Resumes"], summary="Clear all uploaded resumes")
async def clear_resumes():
    _resume_store.clear()
    return {"message": "All resumes cleared."}


@app.post(
    "/api/screen",
    response_model=ScreenResponse,
    tags=["Screening"],
    summary="Screen resumes against a job description",
)
async def screen_resumes(req: ScreenRequest):
    """
    Rank all uploaded resumes against the provided job description
    using weighted scoring (skills, semantic, experience, education)
    and return explainable results.
    """
    if not _resume_store:
        raise HTTPException(
            status_code=400,
            detail="No resumes uploaded. Use /api/upload-resume first.",
        )

    if req.model_name not in settings.AVAILABLE_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model '{req.model_name}'. "
            f"Available: {settings.AVAILABLE_MODELS}",
        )

    filenames = list(_resume_store.keys())
    resume_texts = [_resume_store[fn].clean_text for fn in filenames]
    jd_text = req.job_description

    # Semantic similarity
    emb = EmbeddingManager(req.model_name)
    sem_scores = emb.semantic_similarity(jd_text, resume_texts)

    # Weighted scoring + explainability
    scorer = ResumeScorer()
    explainer = ResumeExplainer()
    candidates: list[CandidateResult] = []

    for i, fname in enumerate(filenames):
        result = scorer.score(
            resume_text=resume_texts[i],
            jd_text=jd_text,
            semantic_sim=float(sem_scores[i]),
            filename=fname,
        )
        expl = explainer.explain(result)
        candidates.append(
            CandidateResult(
                rank=0,  # will be set after sorting
                filename=fname,
                final_score=round(result.final_score * 100, 2),
                verdict=expl.verdict,
                summary=expl.summary,
                strengths=expl.strengths,
                weaknesses=expl.weaknesses,
                matched_skills=expl.matched_skills,
                missing_skills=expl.missing_skills,
                score_breakdown=ScoreBreakdown(**expl.score_breakdown),
            )
        )

    # Sort by score descending & assign ranks
    candidates.sort(key=lambda c: c.final_score, reverse=True)
    for rank, c in enumerate(candidates, 1):
        c.rank = rank

    top = candidates[: req.top_n]

    return ScreenResponse(
        model_used=req.model_name,
        total_resumes=len(filenames),
        candidates=top,
    )


@app.post(
    "/api/compare-models",
    response_model=CompareModelsResponse,
    tags=["Evaluation"],
    summary="Compare TF-IDF vs Transformer models",
)
async def compare_models(req: CompareModelsRequest):
    """
    Run all available models on the uploaded resumes and return
    a comparison including scores, rankings, and timing.
    """
    if not _resume_store:
        raise HTTPException(
            status_code=400,
            detail="No resumes uploaded. Use /api/upload-resume first.",
        )

    filenames = list(_resume_store.keys())
    resume_texts = [_resume_store[fn].clean_text for fn in filenames]

    evaluator = ModelEvaluator()
    report = evaluator.compare(
        job_description=req.job_description,
        resume_texts=resume_texts,
        resume_filenames=filenames,
    )

    return CompareModelsResponse(
        resume_filenames=report.resume_filenames,
        models=[
            ModelBenchmarkResponse(**bm.to_dict()) for bm in report.benchmarks
        ],
        ndcg_scores=report.ndcg_scores,
    )


# ── Run directly ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )

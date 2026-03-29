"""
Pydantic request / response schemas for the Resume Screening API.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


# ── Requests ───────────────────────────────────────────────────────────────


class ScreenRequest(BaseModel):
    job_description: str = Field(
        ..., min_length=10, description="Job description text"
    )
    model_name: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence Transformer model to use",
    )
    top_n: int = Field(
        default=5, ge=1, le=50, description="Number of top candidates to return"
    )


class CompareModelsRequest(BaseModel):
    job_description: str = Field(..., min_length=10)


# ── Responses ──────────────────────────────────────────────────────────────


class ScoreBreakdown(BaseModel):
    skills: float
    semantic: float
    experience: float
    education: float


class CandidateResult(BaseModel):
    rank: int
    filename: str
    final_score: float
    verdict: str
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    score_breakdown: ScoreBreakdown


class ScreenResponse(BaseModel):
    model_used: str
    total_resumes: int
    candidates: list[CandidateResult]


class UploadResponse(BaseModel):
    message: str
    filename: str
    skills_found: list[str]
    experience_years: int
    education: list[str]


class ModelBenchmarkResponse(BaseModel):
    model: str
    scores: list[float]
    ranking: list[int]
    time_seconds: float


class CompareModelsResponse(BaseModel):
    resume_filenames: list[str]
    models: list[ModelBenchmarkResponse]
    ndcg_scores: dict[str, float]


class ErrorResponse(BaseModel):
    detail: str

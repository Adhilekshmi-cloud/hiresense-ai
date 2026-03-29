"""
Weighted scoring system for resume-to-job-description matching.

Components
----------
- Skills Match      (40%) — overlap between extracted skills and JD skills
- Semantic Score    (30%) — embedding cosine similarity
- Experience Match  (20%) — years of experience vs JD requirement
- Education Match   (10%) — degree/field relevance
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.config import settings
from core.text_cleaner import extract_skills, extract_experience_years, extract_education


@dataclass
class ScoringResult:
    """Detailed scoring breakdown for a single resume."""

    filename: str
    final_score: float = 0.0

    # Individual component scores (0–1 scale)
    skills_score: float = 0.0
    semantic_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0

    # Detail data
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    resume_skills: list[str] = field(default_factory=list)
    jd_skills: list[str] = field(default_factory=list)
    resume_experience_years: int = 0
    jd_experience_years: int = 0
    resume_education: list[str] = field(default_factory=list)
    jd_education: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "final_score": round(self.final_score * 100, 2),
            "skills_score": round(self.skills_score * 100, 2),
            "semantic_score": round(self.semantic_score * 100, 2),
            "experience_score": round(self.experience_score * 100, 2),
            "education_score": round(self.education_score * 100, 2),
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "resume_experience_years": self.resume_experience_years,
            "jd_experience_years": self.jd_experience_years,
        }


class ResumeScorer:
    """
    Computes a weighted final score for each resume against a job description.
    """

    def __init__(
        self,
        weight_skills: Optional[float] = None,
        weight_semantic: Optional[float] = None,
        weight_experience: Optional[float] = None,
        weight_education: Optional[float] = None,
    ) -> None:
        self.w_skills = weight_skills if weight_skills is not None else settings.WEIGHT_SKILLS
        self.w_semantic = weight_semantic if weight_semantic is not None else settings.WEIGHT_SEMANTIC
        self.w_experience = weight_experience if weight_experience is not None else settings.WEIGHT_EXPERIENCE
        self.w_education = weight_education if weight_education is not None else settings.WEIGHT_EDUCATION

    # ── Public API ─────────────────────────────────────────────────────

    def score(
        self,
        resume_text: str,
        jd_text: str,
        semantic_sim: float,
        filename: str = "",
    ) -> ScoringResult:
        """
        Score a single resume against a job description.

        Parameters
        ----------
        resume_text : str   Cleaned resume text.
        jd_text : str       Cleaned job description text.
        semantic_sim : float   Pre-computed semantic similarity (0-1).
        filename : str       Resume filename for labelling.
        """
        # Extract features
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)
        resume_exp = extract_experience_years(resume_text)
        jd_exp = extract_experience_years(jd_text)
        resume_edu = extract_education(resume_text)
        jd_edu = extract_education(jd_text)

        # Compute individual scores
        skills_score = self._skills_match(resume_skills, jd_skills)
        experience_score = self._experience_match(resume_exp, jd_exp)
        education_score = self._education_match(resume_edu, jd_edu)
        semantic_score = float(semantic_sim)

        # Weighted final score
        final = (
            self.w_skills * skills_score
            + self.w_semantic * semantic_score
            + self.w_experience * experience_score
            + self.w_education * education_score
        )

        matched = sorted(set(resume_skills) & set(jd_skills))
        missing = sorted(set(jd_skills) - set(resume_skills))

        return ScoringResult(
            filename=filename,
            final_score=final,
            skills_score=skills_score,
            semantic_score=semantic_score,
            experience_score=experience_score,
            education_score=education_score,
            matched_skills=matched,
            missing_skills=missing,
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            resume_experience_years=resume_exp,
            jd_experience_years=jd_exp,
            resume_education=resume_edu,
            jd_education=jd_edu,
        )

    # ── Component scorers ──────────────────────────────────────────────

    @staticmethod
    def _skills_match(resume_skills: list[str], jd_skills: list[str]) -> float:
        """Fraction of JD skills found in the resume."""
        if not jd_skills:
            return 1.0 if resume_skills else 0.5
        matched = set(resume_skills) & set(jd_skills)
        return len(matched) / len(jd_skills)

    @staticmethod
    def _experience_match(resume_years: int, jd_years: int) -> float:
        """Score based on how close the resume experience is to JD requirement."""
        if jd_years == 0:
            return 1.0 if resume_years > 0 else 0.5
        if resume_years >= jd_years:
            return 1.0
        return max(resume_years / jd_years, 0.0)

    @staticmethod
    def _education_match(resume_edu: list[str], jd_edu: list[str]) -> float:
        """Score based on overlap between resume education and JD education."""
        if not jd_edu:
            return 1.0 if resume_edu else 0.5
        matched = set(resume_edu) & set(jd_edu)
        return len(matched) / len(jd_edu)

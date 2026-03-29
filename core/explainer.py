"""
Explainability module — generates human-readable explanations
for why a resume was ranked the way it was.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.scoring import ScoringResult


@dataclass
class Explanation:
    """Human-readable explanation for a single resume's screening result."""

    filename: str
    verdict: str  # "STRONG MATCH", "GOOD MATCH", "PARTIAL MATCH", "WEAK MATCH"
    final_score_pct: float
    summary: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    score_breakdown: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "verdict": self.verdict,
            "final_score_pct": self.final_score_pct,
            "summary": self.summary,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "score_breakdown": self.score_breakdown,
        }


class ResumeExplainer:
    """
    Generates structured, human-readable explanations from ScoringResult objects.
    """

    # ── Verdict thresholds ─────────────────────────────────────────────

    THRESHOLDS = [
        (0.75, "STRONG MATCH"),
        (0.55, "GOOD MATCH"),
        (0.35, "PARTIAL MATCH"),
        (0.00, "WEAK MATCH"),
    ]

    def explain(self, result: ScoringResult) -> Explanation:
        """Build a full explanation from a scoring result."""
        verdict = self._verdict(result.final_score)
        pct = round(result.final_score * 100, 2)

        strengths = self._identify_strengths(result)
        weaknesses = self._identify_weaknesses(result)
        summary = self._build_summary(result, verdict)

        return Explanation(
            filename=result.filename,
            verdict=verdict,
            final_score_pct=pct,
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            matched_skills=result.matched_skills,
            missing_skills=result.missing_skills,
            score_breakdown={
                "skills": round(result.skills_score * 100, 2),
                "semantic": round(result.semantic_score * 100, 2),
                "experience": round(result.experience_score * 100, 2),
                "education": round(result.education_score * 100, 2),
            },
        )

    # ── Private helpers ────────────────────────────────────────────────

    def _verdict(self, score: float) -> str:
        for threshold, label in self.THRESHOLDS:
            if score >= threshold:
                return label
        return "WEAK MATCH"

    @staticmethod
    def _identify_strengths(r: ScoringResult) -> list[str]:
        strengths: list[str] = []
        if r.skills_score >= 0.7:
            strengths.append(
                f"Strong skills alignment — {len(r.matched_skills)} of "
                f"{len(r.jd_skills)} required skills matched"
            )
        elif r.skills_score >= 0.4:
            strengths.append(
                f"Moderate skills match — {len(r.matched_skills)} of "
                f"{len(r.jd_skills)} required skills found"
            )

        if r.semantic_score >= 0.7:
            strengths.append(
                "High semantic relevance — resume content closely aligns "
                "with the job description"
            )

        if r.experience_score >= 0.8:
            strengths.append(
                f"Experience meets or exceeds requirement "
                f"({r.resume_experience_years} yrs vs {r.jd_experience_years} yrs required)"
            )

        if r.education_score >= 0.7:
            strengths.append("Education background is a strong match for the role")

        if not strengths:
            strengths.append("Some relevant background detected")

        return strengths

    @staticmethod
    def _identify_weaknesses(r: ScoringResult) -> list[str]:
        weaknesses: list[str] = []

        if r.missing_skills:
            top_missing = r.missing_skills[:5]
            weaknesses.append(
                f"Missing key skills: {', '.join(top_missing)}"
            )

        if r.skills_score < 0.3:
            weaknesses.append("Very low skills overlap with job requirements")

        if r.experience_score < 0.5 and r.jd_experience_years > 0:
            weaknesses.append(
                f"Experience gap — resume shows {r.resume_experience_years} yrs, "
                f"JD requires {r.jd_experience_years} yrs"
            )

        if r.semantic_score < 0.4:
            weaknesses.append(
                "Low semantic similarity — resume content diverges "
                "significantly from the job description"
            )

        return weaknesses

    @staticmethod
    def _build_summary(r: ScoringResult, verdict: str) -> str:
        pct = round(r.final_score * 100, 1)

        if verdict == "STRONG MATCH":
            return (
                f"This candidate is a strong match ({pct}%). "
                f"They possess {len(r.matched_skills)} of the required skills "
                f"and demonstrate high relevance to the role."
            )
        elif verdict == "GOOD MATCH":
            return (
                f"This candidate is a good match ({pct}%). "
                f"They cover several key requirements but may have "
                f"gaps in {len(r.missing_skills)} skill area(s)."
            )
        elif verdict == "PARTIAL MATCH":
            return (
                f"This candidate is a partial match ({pct}%). "
                f"There are notable gaps in skills or experience "
                f"relative to the job requirements."
            )
        else:
            return (
                f"This candidate is a weak match ({pct}%). "
                f"Significant misalignment with the job description "
                f"across multiple scoring dimensions."
            )

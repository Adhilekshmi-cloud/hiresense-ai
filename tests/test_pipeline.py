"""
Unit tests for the core resume screening modules.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import pytest

from core.text_cleaner import (
    clean_text,
    extract_skills,
    extract_experience_years,
    extract_education,
    process_resume,
)
from core.scoring import ResumeScorer
from core.explainer import ResumeExplainer


# ── Text Cleaner Tests ─────────────────────────────────────────────────────

class TestTextCleaner:
    def test_clean_text_removes_excess_whitespace(self):
        raw = "Hello    world\n\n\n\nfoo"
        result = clean_text(raw)
        assert "    " not in result
        assert "\n\n\n\n" not in result

    def test_extract_skills_finds_python(self):
        text = "I am experienced in Python and machine learning."
        skills = extract_skills(text)
        assert "python" in skills
        assert "machine learning" in skills

    def test_extract_skills_case_insensitive(self):
        text = "Expert in PYTORCH and TensorFlow"
        skills = extract_skills(text)
        assert "pytorch" in skills
        assert "tensorflow" in skills

    def test_extract_experience_years(self):
        text = "I have 5 years of experience in data science."
        assert extract_experience_years(text) == 5

    def test_extract_experience_years_plus(self):
        text = "3+ years experience in Python"
        assert extract_experience_years(text) == 3

    def test_extract_experience_years_none(self):
        text = "Fresh graduate looking for opportunities."
        assert extract_experience_years(text) == 0

    def test_extract_education_finds_degrees(self):
        text = "B.Tech in Computer Science from IIT"
        edu = extract_education(text)
        assert any("computer science" in e for e in edu)

    def test_process_resume_returns_resume_data(self):
        text = "Python developer with 3 years of experience. Skills: Python, Django, SQL."
        rd = process_resume(text, filename="test.txt")
        assert rd.filename == "test.txt"
        assert "python" in rd.skills
        assert rd.experience_years == 3


# ── Scoring Tests ──────────────────────────────────────────────────────────

class TestScoring:
    def test_perfect_match_scores_high(self):
        scorer = ResumeScorer()
        resume = "Python developer with 5 years experience in machine learning and NLP"
        jd = "Looking for a Python developer with 3 years experience in machine learning"
        result = scorer.score(resume, jd, semantic_sim=0.85, filename="test.txt")
        assert result.final_score > 0.5

    def test_no_match_scores_low(self):
        scorer = ResumeScorer()
        resume = "Chef with 10 years culinary experience in Italian cuisine"
        jd = "Looking for a Python developer with machine learning experience"
        result = scorer.score(resume, jd, semantic_sim=0.1, filename="chef.txt")
        assert result.final_score < 0.4

    def test_scoring_result_has_matched_skills(self):
        scorer = ResumeScorer()
        resume = "Skilled in Python, pandas, and numpy for data analysis"
        jd = "Requires Python and pandas experience"
        result = scorer.score(resume, jd, semantic_sim=0.7, filename="test.txt")
        assert "python" in result.matched_skills
        assert "pandas" in result.matched_skills


# ── Explainer Tests ────────────────────────────────────────────────────────

class TestExplainer:
    def test_strong_match_verdict(self):
        scorer = ResumeScorer()
        explainer = ResumeExplainer()
        resume = "Python machine learning NLP expert with 5 years experience"
        jd = "Python machine learning NLP developer needed"
        result = scorer.score(resume, jd, semantic_sim=0.9, filename="test.txt")
        expl = explainer.explain(result)
        assert expl.verdict in ("STRONG MATCH", "GOOD MATCH")
        assert expl.final_score_pct > 50

    def test_explanation_has_summary(self):
        scorer = ResumeScorer()
        explainer = ResumeExplainer()
        resume = "Basic HTML CSS developer"
        jd = "Python machine learning developer"
        result = scorer.score(resume, jd, semantic_sim=0.2, filename="test.txt")
        expl = explainer.explain(result)
        assert len(expl.summary) > 0
        assert expl.filename == "test.txt"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

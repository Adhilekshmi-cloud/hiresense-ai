"""
Text cleaning and structured section extraction from resume text.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ResumeData:
    """Structured representation of a parsed resume."""

    raw_text: str
    clean_text: str = ""
    skills: list[str] = field(default_factory=list)
    experience_years: int = 0
    education: list[str] = field(default_factory=list)
    filename: str = ""


# ── Common skill keywords (extendable) ─────────────────────────────────────

SKILL_KEYWORDS: set[str] = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql", "bash",
    # Web
    "html", "css", "react", "angular", "vue", "node.js", "express",
    "django", "flask", "fastapi", "spring", "next.js", "tailwind",
    # Data / ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "hugging face",
    "transformers", "bert", "gpt", "llm", "data science", "data analysis",
    "data engineering", "feature engineering", "model deployment",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
    "terraform", "ansible", "linux", "git", "github", "gitlab",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "sqlite", "oracle", "cassandra", "dynamodb",
    # Other
    "agile", "scrum", "rest api", "graphql", "microservices",
    "unit testing", "pytest", "jira", "confluence", "power bi", "tableau",
    "excel", "communication", "leadership", "project management",
}

# ── Education keywords ─────────────────────────────────────────────────────

EDUCATION_KEYWORDS: list[str] = [
    "phd", "ph.d", "doctorate",
    "master", "m.s.", "m.sc", "mba", "m.tech", "mtech",
    "bachelor", "b.s.", "b.sc", "b.tech", "btech", "b.e.",
    "diploma", "associate",
    "computer science", "information technology", "engineering",
    "data science", "artificial intelligence", "mathematics",
    "statistics", "physics", "electronics",
]


def clean_text(raw: str) -> str:
    """Normalize whitespace, remove non-printable chars and excess symbols."""
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    # Remove non-printable characters (keep newlines & tabs)
    text = re.sub(r"[^\x20-\x7E\n\t]", " ", text)
    # Collapse multiple newlines / spaces
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def extract_skills(text: str) -> list[str]:
    """Return list of known skills found in resume text."""
    lower = text.lower()
    found: list[str] = []
    for skill in sorted(SKILL_KEYWORDS):
        # Use word-boundary matching for short keywords
        if len(skill) <= 3:
            if re.search(rf"\b{re.escape(skill)}\b", lower):
                found.append(skill)
        else:
            if skill in lower:
                found.append(skill)
    return found


def extract_experience_years(text: str) -> int:
    """Extract the maximum number of years of experience mentioned."""
    patterns = [
        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)?",
        r"experience\s*[:\-]?\s*(\d+)\s*(?:years?|yrs?)",
    ]
    years: list[int] = []
    lower = text.lower()
    for pat in patterns:
        matches = re.findall(pat, lower)
        years.extend(int(m) for m in matches)
    return max(years, default=0)


def extract_education(text: str) -> list[str]:
    """Extract education-related lines/phrases from the resume."""
    lower = text.lower()
    found: list[str] = []
    for kw in EDUCATION_KEYWORDS:
        if kw in lower:
            found.append(kw)
    return list(set(found))


def process_resume(raw_text: str, filename: str = "") -> ResumeData:
    """
    Full processing pipeline: clean text → extract skills, experience, education.
    """
    cleaned = clean_text(raw_text)
    return ResumeData(
        raw_text=raw_text,
        clean_text=cleaned,
        skills=extract_skills(cleaned),
        experience_years=extract_experience_years(cleaned),
        education=extract_education(cleaned),
        filename=filename,
    )

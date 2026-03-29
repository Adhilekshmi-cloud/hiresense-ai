"""
Application configuration — loads from environment variables or .env file.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")


class Settings:
    """Centralized configuration for the Resume Screening system."""

    # ── Model ──────────────────────────────────────────────
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "all-MiniLM-L6-v2")
    AVAILABLE_MODELS: list[str] = [
        "all-MiniLM-L6-v2",
        "all-mpnet-base-v2",
    ]

    # ── Scoring weights (must sum to 1.0) ──────────────────
    WEIGHT_SKILLS: float = float(os.getenv("WEIGHT_SKILLS", "0.40"))
    WEIGHT_SEMANTIC: float = float(os.getenv("WEIGHT_SEMANTIC", "0.30"))
    WEIGHT_EXPERIENCE: float = float(os.getenv("WEIGHT_EXPERIENCE", "0.20"))
    WEIGHT_EDUCATION: float = float(os.getenv("WEIGHT_EDUCATION", "0.10"))

    # ── API ────────────────────────────────────────────────
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))

    # ── Paths ──────────────────────────────────────────────
    PROJECT_ROOT: Path = _project_root
    UPLOAD_DIR: Path = _project_root / "uploads"

    def __init__(self) -> None:
        self.UPLOAD_DIR.mkdir(exist_ok=True)


settings = Settings()

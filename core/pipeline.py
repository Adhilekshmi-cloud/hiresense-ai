"""
Resume parsing pipeline — extracts text from PDF, DOCX, and TXT files.
Handles corrupted and empty files gracefully.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Union

import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Raised when a resume file cannot be parsed."""


def parse_resume(source: Union[str, Path, bytes], filename: str = "") -> str:
    """
    Parse a resume file and return its raw text content.

    Parameters
    ----------
    source : str | Path | bytes
        File path *or* raw file bytes.
    filename : str
        Original filename (used to determine format when *source* is bytes).

    Returns
    -------
    str
        Extracted plain text.

    Raises
    ------
    ParseError
        If the file format is unsupported or the file is unreadable.
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        filename = filename or path.name
        raw_bytes = path.read_bytes()
    else:
        raw_bytes = source

    ext = Path(filename).suffix.lower()

    try:
        if ext == ".txt":
            text = raw_bytes.decode("utf-8", errors="ignore")
        elif ext == ".pdf":
            text = _parse_pdf(raw_bytes)
        elif ext == ".docx":
            text = _parse_docx(raw_bytes)
        else:
            raise ParseError(
                f"Unsupported file format '{ext}'. Accepted: .txt, .pdf, .docx"
            )
    except ParseError:
        raise
    except Exception as exc:
        logger.exception("Failed to parse %s", filename)
        raise ParseError(f"Could not parse '{filename}': {exc}") from exc

    text = text.strip()
    if not text:
        raise ParseError(f"No text content extracted from '{filename}'.")

    return text


# ── Private helpers ────────────────────────────────────────────────────────


def _parse_pdf(data: bytes) -> str:
    """Extract text from a PDF byte stream."""
    pages: list[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                pages.append(page_text)
    return "\n".join(pages)


def _parse_docx(data: bytes) -> str:
    """Extract text from a DOCX byte stream."""
    doc = Document(io.BytesIO(data))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

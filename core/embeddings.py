"""
Embedding manager — supports multiple Sentence Transformer models
and TF-IDF for baseline comparison.
"""
from __future__ import annotations

import time
import logging
from functools import lru_cache
from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


# ── Lazy model loader (cached per model name) ──────────────────────────────

@lru_cache(maxsize=4)
def _load_sentence_model(model_name: str):
    """Load a SentenceTransformer model (cached after first load)."""
    from sentence_transformers import SentenceTransformer
    logger.info("Loading model: %s", model_name)
    return SentenceTransformer(model_name)


class EmbeddingManager:
    """
    Manages embedding generation and similarity computation.

    Supports:
      • Sentence Transformer models (semantic)
      • TF-IDF baseline (keyword-based)
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._tfidf_vectorizer: Optional[TfidfVectorizer] = None

    # ── Sentence Transformer ───────────────────────────────────────────

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encode texts using the configured Sentence Transformer model."""
        model = _load_sentence_model(self.model_name)
        return model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

    def semantic_similarity(
        self, query: str, documents: list[str]
    ) -> np.ndarray:
        """
        Compute cosine similarity between a query and a list of documents.

        Returns
        -------
        np.ndarray
            1-D array of similarity scores in [0, 1] (one per document).
        """
        all_texts = [query] + documents
        embeddings = self.encode(all_texts)
        query_emb = embeddings[0:1]
        doc_embs = embeddings[1:]
        scores = cosine_similarity(query_emb, doc_embs)[0]
        return np.clip(scores, 0, 1)

    def semantic_similarity_timed(
        self, query: str, documents: list[str]
    ) -> tuple[np.ndarray, float]:
        """Same as semantic_similarity but also returns elapsed time."""
        t0 = time.perf_counter()
        scores = self.semantic_similarity(query, documents)
        elapsed = time.perf_counter() - t0
        return scores, elapsed

    # ── TF-IDF Baseline ────────────────────────────────────────────────

    def tfidf_similarity(
        self, query: str, documents: list[str]
    ) -> np.ndarray:
        """Compute TF-IDF + cosine similarity (keyword baseline)."""
        self._tfidf_vectorizer = TfidfVectorizer(stop_words="english")
        all_texts = [query] + documents
        tfidf_matrix = self._tfidf_vectorizer.fit_transform(all_texts)
        scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
        return np.clip(scores, 0, 1)

    def tfidf_similarity_timed(
        self, query: str, documents: list[str]
    ) -> tuple[np.ndarray, float]:
        """Same as tfidf_similarity but also returns elapsed time."""
        t0 = time.perf_counter()
        scores = self.tfidf_similarity(query, documents)
        elapsed = time.perf_counter() - t0
        return scores, elapsed

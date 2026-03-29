"""
Model evaluation and comparison module.

Compares TF-IDF baseline against Sentence Transformer models
using ranking metrics and timing benchmarks.
"""
from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field

import numpy as np

from core.embeddings import EmbeddingManager

logger = logging.getLogger(__name__)


@dataclass
class ModelBenchmark:
    """Benchmark result for a single model."""

    model_name: str
    scores: list[float] = field(default_factory=list)
    ranking: list[int] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    def to_dict(self) -> dict:
        return {
            "model": self.model_name,
            "scores": [round(s, 4) for s in self.scores],
            "ranking": self.ranking,
            "time_seconds": round(self.elapsed_seconds, 4),
        }


@dataclass
class ComparisonReport:
    """Full comparison report across models."""

    benchmarks: list[ModelBenchmark] = field(default_factory=list)
    resume_filenames: list[str] = field(default_factory=list)
    ndcg_scores: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "resume_filenames": self.resume_filenames,
            "models": [b.to_dict() for b in self.benchmarks],
            "ndcg_scores": {k: round(v, 4) for k, v in self.ndcg_scores.items()},
        }


class ModelEvaluator:
    """
    Evaluates and compares multiple models on the same resume–JD pair.
    """

    # Models to compare
    TRANSFORMER_MODELS = ["all-MiniLM-L6-v2", "all-mpnet-base-v2"]

    def compare(
        self,
        job_description: str,
        resume_texts: list[str],
        resume_filenames: list[str] | None = None,
        ground_truth_ranking: list[int] | None = None,
    ) -> ComparisonReport:
        """
        Run all models on the same data and produce a comparison report.

        Parameters
        ----------
        job_description : str
        resume_texts : list[str]
        resume_filenames : list[str] | None
        ground_truth_ranking : list[int] | None
            If provided, compute NDCG against this ideal ranking.
            List of 1-based relevance grades (higher = more relevant),
            one per resume in the same order as resume_texts.
        """
        if resume_filenames is None:
            resume_filenames = [f"resume_{i+1}" for i in range(len(resume_texts))]

        report = ComparisonReport(resume_filenames=resume_filenames)

        # ── TF-IDF baseline ────────────────────────────────────────────
        emb = EmbeddingManager()
        tfidf_scores, tfidf_time = emb.tfidf_similarity_timed(
            job_description, resume_texts
        )
        tfidf_ranking = self._scores_to_ranking(tfidf_scores)
        report.benchmarks.append(
            ModelBenchmark(
                model_name="TF-IDF",
                scores=tfidf_scores.tolist(),
                ranking=tfidf_ranking,
                elapsed_seconds=tfidf_time,
            )
        )

        # ── Transformer models ─────────────────────────────────────────
        for model_name in self.TRANSFORMER_MODELS:
            mgr = EmbeddingManager(model_name)
            scores, elapsed = mgr.semantic_similarity_timed(
                job_description, resume_texts
            )
            ranking = self._scores_to_ranking(scores)
            report.benchmarks.append(
                ModelBenchmark(
                    model_name=model_name,
                    scores=scores.tolist(),
                    ranking=ranking,
                    elapsed_seconds=elapsed,
                )
            )

        # ── NDCG computation (if ground truth provided) ────────────────
        if ground_truth_ranking is not None:
            ideal = np.array(ground_truth_ranking, dtype=float)
            for bm in report.benchmarks:
                predicted_order = np.array(bm.ranking) - 1  # 0-indexed
                predicted_relevance = ideal[predicted_order]
                report.ndcg_scores[bm.model_name] = self._ndcg(
                    predicted_relevance, ideal
                )

        return report

    # ── Helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _scores_to_ranking(scores: np.ndarray) -> list[int]:
        """Convert similarity scores to 1-based ranking (highest first)."""
        order = np.argsort(-scores)
        ranking = np.empty_like(order)
        ranking[order] = np.arange(1, len(scores) + 1)
        return ranking.tolist()

    @staticmethod
    def _dcg(relevances: np.ndarray) -> float:
        """Discounted cumulative gain."""
        positions = np.arange(1, len(relevances) + 1)
        return float(np.sum(relevances / np.log2(positions + 1)))

    def _ndcg(self, predicted: np.ndarray, ideal: np.ndarray) -> float:
        """Normalized discounted cumulative gain (0–1)."""
        ideal_sorted = np.sort(ideal)[::-1]
        dcg = self._dcg(predicted)
        idcg = self._dcg(ideal_sorted)
        if idcg == 0:
            return 0.0
        return dcg / idcg

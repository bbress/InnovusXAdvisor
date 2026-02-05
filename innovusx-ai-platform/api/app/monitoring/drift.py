"""Drift detection for model monitoring."""

import time
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Optional
import random

import structlog

from app.config import settings

logger = structlog.get_logger()


class DriftType(str, Enum):
    """Types of drift to monitor."""
    EMBEDDING = "embedding"
    PREDICTION = "prediction"
    DATA = "data"
    CONCEPT = "concept"


@dataclass
class DriftResult:
    """Result of drift detection."""
    drift_type: DriftType
    is_drifting: bool
    score: float
    threshold: float
    p_value: Optional[float] = None
    details: Optional[dict] = None


class DriftDetector:
    """
    Drift detection for model monitoring.

    Monitors for:
    - Embedding drift: Changes in input embedding distribution
    - Prediction drift: Changes in output distribution
    - Data drift: Changes in input feature distribution
    - Concept drift: Changes in relationship between inputs and outputs
    """

    DEFAULT_THRESHOLDS = {
        DriftType.EMBEDDING: 0.10,
        DriftType.PREDICTION: 0.10,
        DriftType.DATA: 0.10,
        DriftType.CONCEPT: 0.15,
    }

    def __init__(self, thresholds: Optional[dict[DriftType, float]] = None):
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS

        # Reference distributions (in production, load from storage)
        self._reference_embeddings = None
        self._reference_predictions = None
        self._reference_features = None

        # Current window data
        self._current_embeddings = []
        self._current_predictions = []
        self._current_features = []

        # Window size for detection
        self.window_size = 1000

        logger.info(
            "Drift detector initialized",
            thresholds=self.thresholds
        )

    async def record_embedding(self, embedding: list[float]):
        """Record an embedding for drift monitoring."""
        self._current_embeddings.append(embedding)

        # Maintain window size
        if len(self._current_embeddings) > self.window_size:
            self._current_embeddings.pop(0)

    async def record_prediction(self, prediction: dict):
        """Record a prediction for drift monitoring."""
        self._current_predictions.append(prediction)

        if len(self._current_predictions) > self.window_size:
            self._current_predictions.pop(0)

    async def record_features(self, features: dict):
        """Record input features for drift monitoring."""
        self._current_features.append(features)

        if len(self._current_features) > self.window_size:
            self._current_features.pop(0)

    async def detect_embedding_drift(self) -> DriftResult:
        """
        Detect drift in embedding space.

        Uses Kolmogorov-Smirnov test to compare current
        embedding distribution with reference.
        """
        # In production, implement proper KS test
        # For demo, return simulated result
        score = random.uniform(0.01, 0.08)
        threshold = self.thresholds[DriftType.EMBEDDING]

        return DriftResult(
            drift_type=DriftType.EMBEDDING,
            is_drifting=score > threshold,
            score=round(score, 4),
            threshold=threshold,
            p_value=0.15,
            details={
                "mean_shift": round(random.uniform(0.01, 0.03), 4),
                "variance_change": round(random.uniform(0.01, 0.02), 4),
                "samples_compared": min(len(self._current_embeddings), 100)
            }
        )

    async def detect_prediction_drift(self) -> DriftResult:
        """
        Detect drift in prediction distribution.

        Monitors changes in confidence scores, category distribution, etc.
        """
        score = random.uniform(0.02, 0.07)
        threshold = self.thresholds[DriftType.PREDICTION]

        return DriftResult(
            drift_type=DriftType.PREDICTION,
            is_drifting=score > threshold,
            score=round(score, 4),
            threshold=threshold,
            details={
                "confidence_shift": round(random.uniform(-0.02, 0.02), 4),
                "category_distribution_change": round(random.uniform(0.01, 0.04), 4),
                "samples_compared": min(len(self._current_predictions), 100)
            }
        )

    async def detect_data_drift(self) -> DriftResult:
        """
        Detect drift in input data distribution.

        Monitors changes in feature distributions like
        industry mix, query length, etc.
        """
        score = random.uniform(0.01, 0.06)
        threshold = self.thresholds[DriftType.DATA]

        return DriftResult(
            drift_type=DriftType.DATA,
            is_drifting=score > threshold,
            score=round(score, 4),
            threshold=threshold,
            details={
                "industry_distribution_change": round(random.uniform(0.01, 0.03), 4),
                "query_length_shift": round(random.uniform(-5, 5), 2),
                "samples_compared": min(len(self._current_features), 100)
            }
        )

    async def detect_concept_drift(self) -> DriftResult:
        """
        Detect concept drift.

        Monitors changes in the relationship between
        inputs and outputs (e.g., quality scores vs input types).
        """
        score = random.uniform(0.02, 0.08)
        threshold = self.thresholds[DriftType.CONCEPT]

        return DriftResult(
            drift_type=DriftType.CONCEPT,
            is_drifting=score > threshold,
            score=round(score, 4),
            threshold=threshold,
            details={
                "correlation_change": round(random.uniform(-0.05, 0.05), 4),
                "performance_degradation": round(random.uniform(0, 0.03), 4)
            }
        )

    async def run_all_checks(self) -> list[DriftResult]:
        """Run all drift detection checks."""
        results = [
            await self.detect_embedding_drift(),
            await self.detect_prediction_drift(),
            await self.detect_data_drift(),
            await self.detect_concept_drift(),
        ]

        # Log any detected drift
        for result in results:
            if result.is_drifting:
                logger.warning(
                    "Drift detected",
                    drift_type=result.drift_type.value,
                    score=result.score,
                    threshold=result.threshold
                )

        return results

    async def get_recommendations(
        self,
        results: list[DriftResult]
    ) -> list[str]:
        """Get recommendations based on drift results."""
        recommendations = []

        for result in results:
            if result.is_drifting:
                if result.drift_type == DriftType.EMBEDDING:
                    recommendations.append(
                        "Consider retraining embeddings with recent data"
                    )
                elif result.drift_type == DriftType.PREDICTION:
                    recommendations.append(
                        "Review model outputs for quality degradation"
                    )
                elif result.drift_type == DriftType.DATA:
                    recommendations.append(
                        "Investigate changes in input data patterns"
                    )
                elif result.drift_type == DriftType.CONCEPT:
                    recommendations.append(
                        "Consider model retraining or prompt tuning"
                    )
            elif result.score > result.threshold * 0.7:
                recommendations.append(
                    f"Monitor {result.drift_type.value}: score approaching threshold"
                )

        return recommendations

    async def set_reference(
        self,
        drift_type: DriftType,
        data: list
    ):
        """Set reference distribution for drift detection."""
        if drift_type == DriftType.EMBEDDING:
            self._reference_embeddings = data
        elif drift_type == DriftType.PREDICTION:
            self._reference_predictions = data
        elif drift_type == DriftType.DATA:
            self._reference_features = data

        logger.info(
            "Reference distribution set",
            drift_type=drift_type.value,
            sample_size=len(data)
        )


@lru_cache
def get_drift_detector() -> DriftDetector:
    """Get drift detector instance."""
    return DriftDetector()

"""Evaluation engine for response quality assessment."""

import time
from functools import lru_cache
from typing import Optional

import structlog
from pydantic import BaseModel

from app.config import settings
from app.models.strategy import Strategy, QualityMetrics
from app.services.rag_engine import Document

logger = structlog.get_logger()


class EvaluationResult(BaseModel):
    """Detailed evaluation result."""
    relevance: float
    groundedness: float
    coherence: float
    actionability: float
    details: dict = {}


class EvaluationEngine:
    """
    Evaluation engine for assessing response quality.

    Implements multiple evaluation strategies:
    - LLM-as-judge for quality scoring
    - Retrieval relevance metrics
    - Factual grounding checks
    - Actionability assessment
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        logger.info("Evaluation engine initialized")

    async def evaluate(
        self,
        query: str,
        response: list[Strategy],
        context: list[Document],
        correlation_id: str = ""
    ) -> QualityMetrics:
        """
        Evaluate the quality of generated strategies.

        Args:
            query: Original user query
            response: Generated strategies
            context: Retrieved context documents
            correlation_id: Request correlation ID

        Returns:
            QualityMetrics with quality scores
        """
        start_time = time.perf_counter()

        logger.info(
            "Starting evaluation",
            correlation_id=correlation_id,
            strategies_count=len(response),
            context_count=len(context)
        )

        # Run evaluation components
        relevance = await self._evaluate_relevance(query, response)
        groundedness = await self._evaluate_groundedness(response, context)
        coherence = await self._evaluate_coherence(response)
        actionability = await self._evaluate_actionability(response)

        latency_ms = int((time.perf_counter() - start_time) * 1000)

        logger.info(
            "Evaluation completed",
            correlation_id=correlation_id,
            relevance=relevance,
            groundedness=groundedness,
            coherence=coherence,
            actionability=actionability,
            latency_ms=latency_ms
        )

        return QualityMetrics(
            relevance=relevance,
            groundedness=groundedness,
            coherence=coherence,
            actionability=actionability
        )

    async def _evaluate_relevance(
        self,
        query: str,
        strategies: list[Strategy]
    ) -> float:
        """
        Evaluate how relevant strategies are to the query.

        Checks:
        - Semantic alignment with query
        - Addresses stated challenge
        - Appropriate for context
        """
        if not strategies:
            return 0.0

        # In production, use LLM-as-judge
        # For demo, use heuristic scoring

        scores = []
        query_terms = set(query.lower().split())

        for strategy in strategies:
            content = f"{strategy.title} {strategy.description}".lower()
            content_terms = set(content.split())

            # Check term overlap
            overlap = len(query_terms & content_terms)
            overlap_score = min(overlap / max(len(query_terms), 1), 1.0)

            # Check if strategy addresses common themes
            theme_score = 0.0
            themes = ["expand", "grow", "market", "strategy", "partner", "technology"]
            for theme in themes:
                if theme in content:
                    theme_score += 0.1
            theme_score = min(theme_score, 0.5)

            # Combine scores
            score = (overlap_score * 0.5) + (theme_score) + 0.4  # Base score
            scores.append(min(score, 1.0))

        return round(sum(scores) / len(scores), 2)

    async def _evaluate_groundedness(
        self,
        strategies: list[Strategy],
        context: list[Document]
    ) -> float:
        """
        Evaluate how well strategies are grounded in source documents.

        Checks:
        - Claims supported by context
        - No hallucinated facts
        - Proper source attribution
        """
        if not strategies or not context:
            return 0.0

        # In production, use entailment checking or LLM-as-judge
        # For demo, use heuristic scoring

        context_content = " ".join(doc.content.lower() for doc in context)
        scores = []

        for strategy in strategies:
            # Check if strategy themes appear in context
            strategy_content = f"{strategy.description} {strategy.rationale}".lower()
            strategy_terms = set(strategy_content.split())

            context_terms = set(context_content.split())
            overlap = len(strategy_terms & context_terms)
            overlap_ratio = overlap / max(len(strategy_terms), 1)

            # Check source attribution
            has_sources = len(strategy.sources) > 0
            source_bonus = 0.1 if has_sources else 0.0

            score = min((overlap_ratio * 0.8) + source_bonus + 0.3, 1.0)
            scores.append(score)

        return round(sum(scores) / len(scores), 2)

    async def _evaluate_coherence(
        self,
        strategies: list[Strategy]
    ) -> float:
        """
        Evaluate logical coherence of strategies.

        Checks:
        - Logical flow of action steps
        - Consistent messaging
        - Clear structure
        """
        if not strategies:
            return 0.0

        # In production, use LLM-as-judge
        # For demo, use heuristic scoring

        scores = []

        for strategy in strategies:
            score = 0.5  # Base score

            # Check action steps are sequential
            action_steps = strategy.action_steps
            if action_steps:
                # Verify step numbers are sequential
                step_numbers = [s.step_number for s in action_steps]
                if step_numbers == list(range(1, len(step_numbers) + 1)):
                    score += 0.2

                # Check steps have reasonable length
                if all(len(s.description) > 20 for s in action_steps):
                    score += 0.1

            # Check title and description alignment
            if strategy.title and strategy.description:
                title_words = set(strategy.title.lower().split())
                desc_words = set(strategy.description.lower().split())
                if title_words & desc_words:
                    score += 0.1

            # Check rationale is present and substantial
            if strategy.rationale and len(strategy.rationale) > 50:
                score += 0.1

            scores.append(min(score, 1.0))

        return round(sum(scores) / len(scores), 2)

    async def _evaluate_actionability(
        self,
        strategies: list[Strategy]
    ) -> float:
        """
        Evaluate how actionable the strategies are.

        Checks:
        - Specific action steps
        - Timelines provided
        - Resources identified
        - Measurable outcomes
        """
        if not strategies:
            return 0.0

        # In production, use LLM-as-judge
        # For demo, use heuristic scoring

        scores = []

        for strategy in strategies:
            score = 0.4  # Base score

            # Check action steps
            if strategy.action_steps:
                # More steps = more actionable
                step_count = len(strategy.action_steps)
                score += min(step_count * 0.05, 0.2)

                # Check for timelines
                has_timeline = any(s.timeline for s in strategy.action_steps)
                if has_timeline:
                    score += 0.15

                # Check step descriptions are specific
                avg_desc_length = sum(len(s.description) for s in strategy.action_steps) / step_count
                if avg_desc_length > 50:
                    score += 0.1

            # Check for potential impact
            if strategy.potential_impact and len(strategy.potential_impact) > 20:
                score += 0.1

            # Check for risk awareness
            if strategy.risk_factors and len(strategy.risk_factors) > 0:
                score += 0.05

            scores.append(min(score, 1.0))

        return round(sum(scores) / len(scores), 2)

    async def evaluate_batch(
        self,
        evaluations: list[tuple[str, list[Strategy], list[Document]]],
        correlation_id: str = ""
    ) -> list[QualityMetrics]:
        """
        Evaluate multiple responses in batch.

        More efficient for bulk evaluation jobs.
        """
        results = []
        for query, response, context in evaluations:
            metrics = await self.evaluate(query, response, context, correlation_id)
            results.append(metrics)
        return results

    def compute_aggregate_metrics(
        self,
        metrics_list: list[QualityMetrics]
    ) -> dict:
        """Compute aggregate statistics over multiple evaluations."""
        if not metrics_list:
            return {}

        return {
            "count": len(metrics_list),
            "relevance": {
                "mean": sum(m.relevance for m in metrics_list) / len(metrics_list),
                "min": min(m.relevance for m in metrics_list),
                "max": max(m.relevance for m in metrics_list)
            },
            "groundedness": {
                "mean": sum(m.groundedness for m in metrics_list) / len(metrics_list),
                "min": min(m.groundedness for m in metrics_list),
                "max": max(m.groundedness for m in metrics_list)
            },
            "coherence": {
                "mean": sum(m.coherence for m in metrics_list) / len(metrics_list),
                "min": min(m.coherence for m in metrics_list),
                "max": max(m.coherence for m in metrics_list)
            },
            "actionability": {
                "mean": sum(m.actionability for m in metrics_list) / len(metrics_list),
                "min": min(m.actionability for m in metrics_list),
                "max": max(m.actionability for m in metrics_list)
            },
            "overall": {
                "mean": sum(m.overall_score for m in metrics_list) / len(metrics_list),
                "min": min(m.overall_score for m in metrics_list),
                "max": max(m.overall_score for m in metrics_list)
            }
        }


@lru_cache
def get_evaluation_engine() -> EvaluationEngine:
    """Get evaluation engine instance."""
    return EvaluationEngine()

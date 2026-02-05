"""Strategy generation API endpoints."""

import hashlib
import time
from datetime import datetime
from typing import Optional
import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.config import settings
from app.models.strategy import (
    StrategyRequest,
    StrategyResponse,
    Strategy,
    ActionStep,
    QualityMetrics,
    ResponseMetadata,
    FocusArea,
)
from app.services.rag_engine import RAGEngine, get_rag_engine
from app.services.agents import AgentOrchestrator, get_agent_orchestrator
from app.services.llm_gateway import LLMGateway, get_llm_gateway
from app.services.evaluation import EvaluationEngine, get_evaluation_engine
from app.governance.audit import AuditLogger, get_audit_logger
from app.governance.pii_detector import PIIDetector, get_pii_detector

router = APIRouter(prefix="/strategy")
logger = structlog.get_logger()


def hash_input(data: dict) -> str:
    """Create SHA-256 hash of input data."""
    import json
    content = json.dumps(data, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()


@router.post(
    "/generate",
    response_model=StrategyResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate business strategies",
    description="Generate personalized business strategy recommendations based on context"
)
async def generate_strategy(
    request: Request,
    strategy_request: StrategyRequest,
    rag_engine: RAGEngine = Depends(get_rag_engine),
    agent_orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    llm_gateway: LLMGateway = Depends(get_llm_gateway),
    evaluation_engine: EvaluationEngine = Depends(get_evaluation_engine),
    audit_logger: AuditLogger = Depends(get_audit_logger),
    pii_detector: PIIDetector = Depends(get_pii_detector),
) -> StrategyResponse:
    """
    Generate business strategy recommendations.

    This endpoint orchestrates the full AI pipeline:
    1. PII detection and handling
    2. RAG retrieval for context
    3. Multi-agent strategy generation
    4. Quality evaluation
    5. Audit logging

    Args:
        strategy_request: The strategy generation request

    Returns:
        StrategyResponse with generated strategies and metadata
    """
    correlation_id = getattr(request.state, "correlation_id", f"req-{uuid.uuid4().hex[:12]}")
    start_time = time.perf_counter()

    logger.info(
        "Strategy generation started",
        correlation_id=correlation_id,
        industry=strategy_request.industry.value,
        company_stage=strategy_request.company_stage.value
    )

    try:
        # Step 1: PII Detection
        pii_result = await pii_detector.scan(
            text=strategy_request.challenge + (strategy_request.context or ""),
            correlation_id=correlation_id
        )

        if pii_result.pii_detected and pii_result.action_taken == "blocked":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request contains sensitive personal information that cannot be processed"
            )

        # Use redacted text if PII was found
        safe_challenge = pii_result.redacted_text or strategy_request.challenge

        # Step 2: RAG Retrieval
        retrieval_result = await rag_engine.retrieve(
            query=safe_challenge,
            industry=strategy_request.industry.value,
            focus_area=strategy_request.focus_area.value if strategy_request.focus_area else None,
            k=settings.rag_retrieval_k,
            correlation_id=correlation_id
        )

        # Step 3: Agent Orchestration for Strategy Generation
        agent_result = await agent_orchestrator.generate_strategies(
            request=strategy_request,
            context_documents=retrieval_result.documents,
            correlation_id=correlation_id
        )

        # Step 4: Quality Evaluation
        quality_metrics = await evaluation_engine.evaluate(
            query=strategy_request.challenge,
            response=agent_result.strategies,
            context=retrieval_result.documents,
            correlation_id=correlation_id
        )

        # Calculate timing and costs
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        # Build response
        response = StrategyResponse(
            strategies=agent_result.strategies,
            quality_metrics=quality_metrics,
            metadata=ResponseMetadata(
                correlation_id=correlation_id,
                model_version=agent_result.model_version,
                latency_ms=latency_ms,
                tokens_used=agent_result.tokens_used,
                cost_usd=agent_result.cost_usd,
                cached=retrieval_result.cached,
                retrieval_count=len(retrieval_result.documents)
            ),
            generated_at=datetime.utcnow()
        )

        # Step 5: Audit Logging
        await audit_logger.log_strategy_generation(
            correlation_id=correlation_id,
            request=strategy_request,
            response=response,
            pii_detected=pii_result.pii_detected,
            latency_ms=latency_ms,
            status="success"
        )

        logger.info(
            "Strategy generation completed",
            correlation_id=correlation_id,
            num_strategies=len(response.strategies),
            quality_score=quality_metrics.overall_score,
            latency_ms=latency_ms
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        # Log failure
        await audit_logger.log_strategy_generation(
            correlation_id=correlation_id,
            request=strategy_request,
            response=None,
            pii_detected=False,
            latency_ms=latency_ms,
            status="failure",
            error_message=str(e)
        )

        logger.error(
            "Strategy generation failed",
            correlation_id=correlation_id,
            error=str(e),
            latency_ms=latency_ms
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate strategies. Please try again."
        )


@router.get(
    "/demo",
    response_model=StrategyResponse,
    summary="Demo strategy generation",
    description="Generate demo strategies with mock data for testing"
)
async def demo_strategy(
    request: Request,
    industry: str = "fintech",
    challenge: str = "Expand into new markets"
) -> StrategyResponse:
    """
    Demo endpoint that returns mock strategy data.

    Useful for testing the frontend without consuming LLM tokens.
    """
    correlation_id = getattr(request.state, "correlation_id", f"demo-{uuid.uuid4().hex[:8]}")

    # Generate mock strategies
    strategies = [
        Strategy(
            id=f"str-{uuid.uuid4().hex[:8]}",
            title="Phased Market Entry Strategy",
            category=FocusArea.MARKET_EXPANSION,
            description="Implement a phased approach to market expansion, starting with markets that have strong regulatory alignment and existing customer demand. Focus on building local partnerships and adapting the product to meet regional requirements.",
            confidence_score=0.92,
            action_steps=[
                ActionStep(
                    step_number=1,
                    title="Market Analysis",
                    description="Conduct comprehensive analysis of target markets including regulatory landscape, competitive environment, and customer needs assessment.",
                    timeline="Weeks 1-4"
                ),
                ActionStep(
                    step_number=2,
                    title="Partnership Development",
                    description="Identify and engage potential local partners including banks, payment processors, and distribution channels.",
                    timeline="Weeks 4-8"
                ),
                ActionStep(
                    step_number=3,
                    title="Regulatory Compliance",
                    description="Prepare and submit necessary regulatory applications. Engage local legal counsel for compliance requirements.",
                    timeline="Weeks 8-16"
                ),
                ActionStep(
                    step_number=4,
                    title="Pilot Launch",
                    description="Launch limited pilot program with selected partners to validate market fit and operational readiness.",
                    timeline="Weeks 16-24"
                ),
                ActionStep(
                    step_number=5,
                    title="Scale Operations",
                    description="Based on pilot results, scale operations with full marketing launch and expanded partner network.",
                    timeline="Weeks 24-36"
                )
            ],
            rationale="A phased approach minimizes risk while allowing for market learning and adaptation. This strategy has proven successful for similar fintech companies entering new geographic markets.",
            potential_impact="Access to 50M+ potential customers with projected 40% revenue increase within 18 months",
            risk_factors=["Regulatory delays", "Currency fluctuation", "Local competition"],
            sources=["market_expansion_guide.md", "fintech_case_studies.md"]
        ),
        Strategy(
            id=f"str-{uuid.uuid4().hex[:8]}",
            title="Strategic Partnership Accelerator",
            category=FocusArea.PARTNERSHIPS,
            description="Leverage strategic partnerships with established financial institutions to accelerate market entry. This approach provides instant credibility, existing customer base access, and regulatory cover.",
            confidence_score=0.87,
            action_steps=[
                ActionStep(
                    step_number=1,
                    title="Partner Identification",
                    description="Create shortlist of potential banking and fintech partners based on strategic fit, market presence, and partnership track record.",
                    timeline="Weeks 1-3"
                ),
                ActionStep(
                    step_number=2,
                    title="Value Proposition Development",
                    description="Develop compelling partnership proposals that clearly articulate mutual benefits and integration possibilities.",
                    timeline="Weeks 3-5"
                ),
                ActionStep(
                    step_number=3,
                    title="Negotiation and Agreement",
                    description="Engage in partnership discussions, negotiate terms, and finalize partnership agreements.",
                    timeline="Weeks 5-12"
                ),
                ActionStep(
                    step_number=4,
                    title="Integration Execution",
                    description="Execute technical and operational integration with partner systems and processes.",
                    timeline="Weeks 12-20"
                )
            ],
            rationale="Strategic partnerships can reduce time-to-market by 50% compared to organic expansion while sharing the risk and investment requirements.",
            potential_impact="Potential to reach 10M customers through partner networks within first year",
            risk_factors=["Partner dependency", "Integration complexity", "Revenue sharing impact"],
            sources=["partnership_strategies.md", "fintech_partnerships.md"]
        ),
        Strategy(
            id=f"str-{uuid.uuid4().hex[:8]}",
            title="Digital-First Market Penetration",
            category=FocusArea.TECHNOLOGY,
            description="Deploy a fully digital market entry strategy leveraging cloud infrastructure, API-first architecture, and data-driven customer acquisition to minimize physical presence requirements.",
            confidence_score=0.84,
            action_steps=[
                ActionStep(
                    step_number=1,
                    title="Infrastructure Setup",
                    description="Deploy cloud infrastructure in target region with full compliance and data residency requirements.",
                    timeline="Weeks 1-6"
                ),
                ActionStep(
                    step_number=2,
                    title="Digital Product Adaptation",
                    description="Localize product for target market including language, currency, and regulatory requirements.",
                    timeline="Weeks 4-10"
                ),
                ActionStep(
                    step_number=3,
                    title="Digital Marketing Launch",
                    description="Execute comprehensive digital marketing campaign targeting key customer segments through social, search, and content channels.",
                    timeline="Weeks 10-14"
                ),
                ActionStep(
                    step_number=4,
                    title="Performance Optimization",
                    description="Continuously optimize acquisition channels, conversion funnels, and customer experience based on data insights.",
                    timeline="Ongoing"
                )
            ],
            rationale="Digital-first approach enables rapid iteration and scaling while maintaining cost efficiency. Particularly effective for tech-savvy customer segments.",
            potential_impact="30% lower customer acquisition cost compared to traditional market entry",
            risk_factors=["Digital adoption variations", "Brand awareness challenges", "Support scalability"],
            sources=["digital_expansion.md", "growth_hacking.md"]
        )
    ]

    return StrategyResponse(
        strategies=strategies,
        quality_metrics=QualityMetrics(
            relevance=0.89,
            groundedness=0.91,
            coherence=0.88,
            actionability=0.85
        ),
        metadata=ResponseMetadata(
            correlation_id=correlation_id,
            model_version="demo-v1.0",
            latency_ms=150,
            tokens_used=0,
            cost_usd=0.0,
            cached=True,
            retrieval_count=6
        ),
        generated_at=datetime.utcnow()
    )

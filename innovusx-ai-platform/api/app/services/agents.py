"""Multi-agent orchestration system."""

import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from functools import lru_cache

import structlog
from pydantic import BaseModel

from app.config import settings
from app.models.strategy import (
    Strategy,
    StrategyRequest,
    ActionStep,
    FocusArea,
)
from app.services.rag_engine import Document

logger = structlog.get_logger()


class AgentType(str, Enum):
    """Types of agents in the system."""
    RESEARCH = "research"
    STRATEGY = "strategy"
    COMPLIANCE = "compliance"


class AgentState(BaseModel):
    """State passed between agents."""
    request: dict
    context_documents: list[dict]
    research_insights: Optional[dict] = None
    draft_strategies: Optional[list[dict]] = None
    validated_strategies: Optional[list[dict]] = None
    compliance_results: Optional[dict] = None


class AgentResult(BaseModel):
    """Result from agent orchestration."""
    strategies: list[Strategy]
    model_version: str
    tokens_used: int
    cost_usd: float
    agent_trace: list[dict]


class ResearchAgent:
    """
    Research Agent: Gathers and synthesizes context.

    Responsibilities:
    - Analyze retrieved documents
    - Extract key insights
    - Identify market trends
    - Summarize competitive landscape
    """

    def __init__(self, llm_gateway):
        self.llm = llm_gateway
        self.agent_type = AgentType.RESEARCH

    async def run(
        self,
        state: AgentState,
        correlation_id: str
    ) -> AgentState:
        """Execute research agent."""
        logger.info(
            "Research agent started",
            correlation_id=correlation_id,
            context_docs=len(state.context_documents)
        )

        # Analyze context documents
        insights = {
            "key_themes": [],
            "market_trends": [],
            "best_practices": [],
            "risk_factors": []
        }

        # In production, use LLM to extract insights
        # For demo, extract from mock documents
        for doc in state.context_documents:
            content = doc.get("content", "")
            if "market" in content.lower():
                insights["market_trends"].append("Market expansion opportunity identified")
            if "partner" in content.lower():
                insights["best_practices"].append("Strategic partnerships recommended")
            if "regul" in content.lower():
                insights["risk_factors"].append("Regulatory compliance required")

        # Add synthesized insights
        insights["key_themes"] = [
            "Digital-first expansion strategy",
            "Partnership-driven growth",
            "Compliance-aware market entry"
        ]

        state.research_insights = insights

        logger.info(
            "Research agent completed",
            correlation_id=correlation_id,
            insights_count=sum(len(v) for v in insights.values())
        )

        return state


class StrategyAgent:
    """
    Strategy Agent: Generates strategy recommendations.

    Responsibilities:
    - Synthesize research insights
    - Generate actionable strategies
    - Create detailed action steps
    - Assess confidence levels
    """

    def __init__(self, llm_gateway):
        self.llm = llm_gateway
        self.agent_type = AgentType.STRATEGY

    async def run(
        self,
        state: AgentState,
        correlation_id: str
    ) -> AgentState:
        """Execute strategy agent."""
        logger.info(
            "Strategy agent started",
            correlation_id=correlation_id
        )

        request = state.request
        insights = state.research_insights or {}
        num_strategies = request.get("num_strategies", 3)

        # In production, use LLM to generate strategies
        # For demo, generate based on request and insights
        strategies = []

        # Strategy templates based on focus area
        strategy_templates = self._get_strategy_templates(
            industry=request.get("industry"),
            focus_area=request.get("focus_area"),
            insights=insights
        )

        for i, template in enumerate(strategy_templates[:num_strategies]):
            strategy = {
                "id": f"str-{uuid.uuid4().hex[:8]}",
                "title": template["title"],
                "category": template["category"],
                "description": template["description"],
                "confidence_score": template["confidence"],
                "action_steps": template["action_steps"],
                "rationale": template["rationale"],
                "potential_impact": template["impact"],
                "risk_factors": template["risks"],
                "sources": [doc.get("source", "") for doc in state.context_documents[:3]]
            }
            strategies.append(strategy)

        state.draft_strategies = strategies

        logger.info(
            "Strategy agent completed",
            correlation_id=correlation_id,
            strategies_generated=len(strategies)
        )

        return state

    def _get_strategy_templates(
        self,
        industry: str,
        focus_area: Optional[str],
        insights: dict
    ) -> list[dict]:
        """Get strategy templates based on context."""
        templates = [
            {
                "title": f"Phased Market Entry for {industry.title() if industry else 'Target'} Expansion",
                "category": FocusArea.MARKET_EXPANSION,
                "description": "Implement a systematic phased approach to market expansion, starting with markets that offer the best combination of opportunity and manageable complexity. This strategy emphasizes building strong local foundations before scaling.",
                "confidence": 0.92,
                "action_steps": [
                    ActionStep(step_number=1, title="Market Prioritization Analysis", description="Evaluate potential markets based on size, competition, regulatory environment, and strategic fit. Create a ranked list of target markets with clear selection criteria.", timeline="Weeks 1-3"),
                    ActionStep(step_number=2, title="Pilot Market Selection", description="Select initial market based on analysis. Develop detailed market entry requirements including regulatory, operational, and resource needs.", timeline="Weeks 3-4"),
                    ActionStep(step_number=3, title="Local Infrastructure Setup", description="Establish necessary local presence including legal entity, banking relationships, and operational infrastructure.", timeline="Weeks 4-12"),
                    ActionStep(step_number=4, title="Soft Launch", description="Execute limited launch with early adopter customers. Collect feedback and iterate on product-market fit.", timeline="Weeks 12-20"),
                    ActionStep(step_number=5, title="Scale and Expand", description="Based on pilot learnings, scale operations in initial market and begin planning for next market entry.", timeline="Weeks 20-36"),
                ],
                "rationale": "Phased expansion reduces risk by validating assumptions in controlled environments before committing significant resources. This approach allows for learning and adaptation while maintaining momentum.",
                "impact": "Expected 30-40% revenue increase within 18 months with manageable risk exposure",
                "risks": ["Slower time-to-market", "Competitor first-mover advantage", "Resource constraints"]
            },
            {
                "title": "Strategic Partnership Accelerator",
                "category": FocusArea.PARTNERSHIPS,
                "description": "Leverage strategic partnerships with established players to accelerate growth. Partners provide distribution, credibility, and operational capabilities that would take years to build organically.",
                "confidence": 0.88,
                "action_steps": [
                    ActionStep(step_number=1, title="Partner Landscape Mapping", description="Identify and evaluate potential partners based on strategic fit, market presence, and partnership track record. Create tiered partner target list.", timeline="Weeks 1-4"),
                    ActionStep(step_number=2, title="Value Proposition Development", description="Develop compelling partnership proposals that clearly articulate mutual benefits, integration approach, and success metrics.", timeline="Weeks 4-6"),
                    ActionStep(step_number=3, title="Partner Engagement", description="Initiate discussions with priority partners. Navigate partnership negotiations with focus on long-term value creation.", timeline="Weeks 6-14"),
                    ActionStep(step_number=4, title="Integration Planning", description="Develop detailed integration roadmap covering technical, operational, and go-to-market aspects.", timeline="Weeks 14-18"),
                    ActionStep(step_number=5, title="Launch and Optimize", description="Execute partnership launch with joint go-to-market activities. Establish partnership governance and continuous improvement processes.", timeline="Weeks 18-26"),
                ],
                "rationale": "Strategic partnerships can compress years of market building into months. The right partner provides immediate access to customers, channels, and capabilities.",
                "impact": "Potential to reach 5-10x more customers within first year compared to organic expansion",
                "risks": ["Partner dependency", "Revenue sharing impact", "Integration complexity", "Cultural alignment"]
            },
            {
                "title": "Technology-Led Differentiation",
                "category": FocusArea.TECHNOLOGY,
                "description": "Invest in technology capabilities that create sustainable competitive advantages. Focus on areas where technology can deliver step-change improvements in customer experience, operational efficiency, or business model innovation.",
                "confidence": 0.85,
                "action_steps": [
                    ActionStep(step_number=1, title="Technology Assessment", description="Evaluate current technology capabilities against market leaders and emerging innovators. Identify high-impact opportunity areas.", timeline="Weeks 1-4"),
                    ActionStep(step_number=2, title="Innovation Roadmap", description="Develop prioritized technology investment roadmap aligned with strategic objectives. Balance quick wins with longer-term capabilities.", timeline="Weeks 4-6"),
                    ActionStep(step_number=3, title="Capability Building", description="Execute technology development through combination of internal build, partnerships, and selective acquisitions.", timeline="Weeks 6-24"),
                    ActionStep(step_number=4, title="Market Validation", description="Launch technology-enabled offerings with lead customers. Gather feedback and demonstrate value.", timeline="Weeks 20-30"),
                    ActionStep(step_number=5, title="Scale and Monetize", description="Scale successful innovations across customer base. Develop technology-based revenue streams.", timeline="Weeks 30-52"),
                ],
                "rationale": "Technology leadership creates defensible competitive moats that are difficult for competitors to replicate quickly. It also enables premium positioning and higher margins.",
                "impact": "20-30% improvement in unit economics through technology-enabled efficiency gains",
                "risks": ["Technology execution risk", "Rapid market change", "Investment requirements"]
            },
        ]

        return templates


class ComplianceAgent:
    """
    Compliance Agent: Validates strategy recommendations.

    Responsibilities:
    - Check for harmful content
    - Validate factual claims
    - Ensure regulatory alignment
    - Assess ethical implications
    """

    def __init__(self, llm_gateway):
        self.llm = llm_gateway
        self.agent_type = AgentType.COMPLIANCE

    async def run(
        self,
        state: AgentState,
        correlation_id: str
    ) -> AgentState:
        """Execute compliance agent."""
        logger.info(
            "Compliance agent started",
            correlation_id=correlation_id,
            strategies_to_validate=len(state.draft_strategies or [])
        )

        validated_strategies = []
        compliance_results = {
            "checks_passed": 0,
            "checks_failed": 0,
            "warnings": []
        }

        for strategy in state.draft_strategies or []:
            # Perform compliance checks
            is_valid, issues = await self._validate_strategy(strategy)

            if is_valid:
                validated_strategies.append(strategy)
                compliance_results["checks_passed"] += 1
            else:
                compliance_results["checks_failed"] += 1
                compliance_results["warnings"].extend(issues)

        state.validated_strategies = validated_strategies
        state.compliance_results = compliance_results

        logger.info(
            "Compliance agent completed",
            correlation_id=correlation_id,
            strategies_validated=len(validated_strategies),
            checks_passed=compliance_results["checks_passed"]
        )

        return state

    async def _validate_strategy(self, strategy: dict) -> tuple[bool, list[str]]:
        """Validate a single strategy."""
        issues = []

        # Check for prohibited content
        prohibited_terms = ["guaranteed returns", "risk-free", "illegal"]
        content = f"{strategy.get('title', '')} {strategy.get('description', '')}"

        for term in prohibited_terms:
            if term.lower() in content.lower():
                issues.append(f"Prohibited term found: {term}")

        # Check confidence score is reasonable
        confidence = strategy.get("confidence_score", 0)
        if confidence > 0.99:
            issues.append("Confidence score unrealistically high")

        # Check action steps are present
        if not strategy.get("action_steps"):
            issues.append("No action steps provided")

        return len(issues) == 0, issues


class AgentOrchestrator:
    """
    Orchestrates multi-agent workflow for strategy generation.

    Workflow:
    1. Research Agent: Analyze context and extract insights
    2. Strategy Agent: Generate strategy recommendations
    3. Compliance Agent: Validate and filter strategies
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        self.research_agent = ResearchAgent(llm_gateway)
        self.strategy_agent = StrategyAgent(llm_gateway)
        self.compliance_agent = ComplianceAgent(llm_gateway)

        logger.info("Agent orchestrator initialized")

    async def generate_strategies(
        self,
        request: StrategyRequest,
        context_documents: list[Document],
        correlation_id: str
    ) -> AgentResult:
        """
        Orchestrate strategy generation across agents.

        Args:
            request: Strategy generation request
            context_documents: Retrieved context documents
            correlation_id: Request correlation ID

        Returns:
            AgentResult with generated strategies
        """
        start_time = time.perf_counter()
        agent_trace = []

        logger.info(
            "Starting agent orchestration",
            correlation_id=correlation_id
        )

        # Initialize state
        state = AgentState(
            request=request.model_dump(),
            context_documents=[doc.model_dump() for doc in context_documents]
        )

        # Run Research Agent
        research_start = time.perf_counter()
        state = await self.research_agent.run(state, correlation_id)
        agent_trace.append({
            "agent": AgentType.RESEARCH.value,
            "latency_ms": int((time.perf_counter() - research_start) * 1000),
            "status": "completed"
        })

        # Run Strategy Agent
        strategy_start = time.perf_counter()
        state = await self.strategy_agent.run(state, correlation_id)
        agent_trace.append({
            "agent": AgentType.STRATEGY.value,
            "latency_ms": int((time.perf_counter() - strategy_start) * 1000),
            "status": "completed"
        })

        # Run Compliance Agent
        compliance_start = time.perf_counter()
        state = await self.compliance_agent.run(state, correlation_id)
        agent_trace.append({
            "agent": AgentType.COMPLIANCE.value,
            "latency_ms": int((time.perf_counter() - compliance_start) * 1000),
            "status": "completed"
        })

        # Convert to Strategy models
        strategies = [
            Strategy(**s) for s in (state.validated_strategies or [])
        ]

        total_latency = int((time.perf_counter() - start_time) * 1000)

        logger.info(
            "Agent orchestration completed",
            correlation_id=correlation_id,
            total_latency_ms=total_latency,
            strategies_generated=len(strategies)
        )

        return AgentResult(
            strategies=strategies,
            model_version="v2.3",
            tokens_used=850,  # Mock token count
            cost_usd=0.04,    # Mock cost
            agent_trace=agent_trace
        )


@lru_cache
def get_agent_orchestrator() -> AgentOrchestrator:
    """Get agent orchestrator instance."""
    return AgentOrchestrator()

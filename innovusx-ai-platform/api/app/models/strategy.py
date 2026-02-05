"""Strategy-related data models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Industry(str, Enum):
    """Supported industry verticals."""
    FINTECH = "fintech"
    HEALTHTECH = "healthtech"
    SAAS = "saas"
    ECOMMERCE = "ecommerce"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    LOGISTICS = "logistics"
    EDUCATION = "education"
    CLEANTECH = "cleantech"
    OTHER = "other"


class CompanyStage(str, Enum):
    """Company growth stages."""
    STARTUP = "startup"
    GROWTH = "growth"
    SCALEUP = "scaleup"
    ENTERPRISE = "enterprise"


class FocusArea(str, Enum):
    """Strategic focus areas."""
    MARKET_EXPANSION = "market_expansion"
    PRODUCT_INNOVATION = "product_innovation"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    REVENUE_GROWTH = "revenue_growth"
    TALENT_DEVELOPMENT = "talent_development"
    PARTNERSHIPS = "partnerships"
    TECHNOLOGY = "technology"


class ActionStep(BaseModel):
    """Individual action step within a strategy."""
    step_number: int = Field(..., ge=1, le=10)
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=20, max_length=500)
    timeline: Optional[str] = Field(None, max_length=50)
    resources_needed: Optional[list[str]] = None


class Strategy(BaseModel):
    """A single strategy recommendation."""
    id: str = Field(..., description="Unique strategy identifier")
    title: str = Field(..., min_length=10, max_length=150)
    category: FocusArea
    description: str = Field(..., min_length=50, max_length=1000)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    action_steps: list[ActionStep] = Field(..., min_length=1, max_length=10)
    rationale: str = Field(..., min_length=50, max_length=500)
    potential_impact: str = Field(..., max_length=200)
    risk_factors: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list, description="Knowledge base sources used")


class QualityMetrics(BaseModel):
    """Quality metrics for the generated response."""
    relevance: float = Field(..., ge=0.0, le=1.0, description="How relevant to the query")
    groundedness: float = Field(..., ge=0.0, le=1.0, description="How grounded in sources")
    coherence: float = Field(..., ge=0.0, le=1.0, description="Logical flow and clarity")
    actionability: float = Field(..., ge=0.0, le=1.0, description="How actionable the advice is")

    @property
    def overall_score(self) -> float:
        """Calculate weighted overall score."""
        weights = {
            "relevance": 0.3,
            "groundedness": 0.25,
            "coherence": 0.2,
            "actionability": 0.25
        }
        return (
            self.relevance * weights["relevance"] +
            self.groundedness * weights["groundedness"] +
            self.coherence * weights["coherence"] +
            self.actionability * weights["actionability"]
        )


class StrategyRequest(BaseModel):
    """Request model for strategy generation."""
    industry: Industry = Field(..., description="Industry vertical")
    company_stage: CompanyStage = Field(..., description="Current company stage")
    challenge: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Primary business challenge or goal"
    )
    focus_area: Optional[FocusArea] = Field(
        None,
        description="Preferred strategic focus area"
    )
    context: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional context about the business"
    )
    num_strategies: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of strategies to generate"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "industry": "fintech",
                    "company_stage": "growth",
                    "challenge": "Expand into European markets while maintaining regulatory compliance",
                    "focus_area": "market_expansion",
                    "context": "B2B payments platform with 50 employees, Series B funded",
                    "num_strategies": 3
                }
            ]
        }
    }


class ResponseMetadata(BaseModel):
    """Metadata about the response generation."""
    correlation_id: str
    model_version: str
    latency_ms: int
    tokens_used: int
    cost_usd: float
    cached: bool = False
    retrieval_count: int = Field(..., description="Number of documents retrieved")


class StrategyResponse(BaseModel):
    """Response model for strategy generation."""
    strategies: list[Strategy]
    quality_metrics: QualityMetrics
    metadata: ResponseMetadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "strategies": [
                        {
                            "id": "str-001",
                            "title": "Phased European Market Entry via UK Gateway",
                            "category": "market_expansion",
                            "description": "Establish UK operations as a beachhead for broader European expansion...",
                            "confidence_score": 0.92,
                            "action_steps": [
                                {
                                    "step_number": 1,
                                    "title": "Regulatory Assessment",
                                    "description": "Conduct comprehensive review of FCA requirements...",
                                    "timeline": "Weeks 1-4"
                                }
                            ],
                            "rationale": "UK provides English-speaking market with clear regulatory framework...",
                            "potential_impact": "Access to 60M+ consumers and gateway to EU markets",
                            "risk_factors": ["Brexit regulatory divergence", "Currency fluctuation"],
                            "sources": ["market_expansion_guide.md", "fintech_regulations_uk.md"]
                        }
                    ],
                    "quality_metrics": {
                        "relevance": 0.94,
                        "groundedness": 0.91,
                        "coherence": 0.89,
                        "actionability": 0.87
                    },
                    "metadata": {
                        "correlation_id": "req-abc123",
                        "model_version": "v2.3",
                        "latency_ms": 1234,
                        "tokens_used": 856,
                        "cost_usd": 0.04,
                        "cached": False,
                        "retrieval_count": 12
                    },
                    "generated_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
    }

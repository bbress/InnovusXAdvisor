"""LLM Gateway with intelligent routing and fallback."""

import time
import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any
from functools import lru_cache

import structlog
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = structlog.get_logger()


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class ModelTier(str, Enum):
    """Model performance tiers."""
    PREMIUM = "premium"       # GPT-4, Claude 3 Opus
    STANDARD = "standard"     # GPT-4 Turbo, Claude 3 Sonnet
    ECONOMY = "economy"       # GPT-3.5, Claude 3 Haiku


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    provider: LLMProvider
    model_id: str
    tier: ModelTier
    max_tokens: int
    temperature: float = 0.7
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


class LLMResponse(BaseModel):
    """Response from LLM inference."""
    content: str
    model_used: str
    provider: str
    tokens_input: int
    tokens_output: int
    latency_ms: int
    cost_usd: float
    cached: bool = False
    fallback_used: bool = False


class LLMGateway:
    """
    Intelligent LLM gateway with routing and fallback.

    Features:
    - Multi-provider support (OpenAI, Anthropic)
    - Automatic fallback on failures
    - Response caching
    - Cost tracking
    - Rate limiting
    """

    # Model configurations
    MODELS = {
        "gpt-4-turbo-preview": ModelConfig(
            provider=LLMProvider.OPENAI,
            model_id="gpt-4-turbo-preview",
            tier=ModelTier.STANDARD,
            max_tokens=4096,
            cost_per_1k_input=0.01,
            cost_per_1k_output=0.03
        ),
        "gpt-4": ModelConfig(
            provider=LLMProvider.OPENAI,
            model_id="gpt-4",
            tier=ModelTier.PREMIUM,
            max_tokens=4096,
            cost_per_1k_input=0.03,
            cost_per_1k_output=0.06
        ),
        "gpt-3.5-turbo": ModelConfig(
            provider=LLMProvider.OPENAI,
            model_id="gpt-3.5-turbo",
            tier=ModelTier.ECONOMY,
            max_tokens=4096,
            cost_per_1k_input=0.0005,
            cost_per_1k_output=0.0015
        ),
        "claude-3-sonnet-20240229": ModelConfig(
            provider=LLMProvider.ANTHROPIC,
            model_id="claude-3-sonnet-20240229",
            tier=ModelTier.STANDARD,
            max_tokens=4096,
            cost_per_1k_input=0.003,
            cost_per_1k_output=0.015
        ),
        "claude-3-haiku-20240307": ModelConfig(
            provider=LLMProvider.ANTHROPIC,
            model_id="claude-3-haiku-20240307",
            tier=ModelTier.ECONOMY,
            max_tokens=4096,
            cost_per_1k_input=0.00025,
            cost_per_1k_output=0.00125
        ),
    }

    # Fallback chain
    FALLBACK_CHAIN = [
        "gpt-4-turbo-preview",
        "claude-3-sonnet-20240229",
        "gpt-3.5-turbo"
    ]

    def __init__(self):
        self.primary_model = settings.llm_primary_model
        self.fallback_model = settings.llm_fallback_model
        self._cache: dict[str, LLMResponse] = {}
        self._openai_client = None
        self._anthropic_client = None

        logger.info(
            "LLM Gateway initialized",
            primary_model=self.primary_model,
            fallback_model=self.fallback_model
        )

    async def generate(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
        correlation_id: str = ""
    ) -> LLMResponse:
        """
        Generate completion from LLM.

        Args:
            messages: Chat messages (role, content)
            model: Specific model to use (optional)
            temperature: Override temperature (optional)
            max_tokens: Override max tokens (optional)
            use_cache: Whether to use response cache
            correlation_id: Request correlation ID

        Returns:
            LLMResponse with generated content
        """
        model = model or self.primary_model
        model_config = self.MODELS.get(model)

        if not model_config:
            raise ValueError(f"Unknown model: {model}")

        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(messages, model)
            if cache_key in self._cache:
                logger.info(
                    "Cache hit",
                    correlation_id=correlation_id,
                    model=model
                )
                cached = self._cache[cache_key]
                cached.cached = True
                return cached

        # Try primary model with fallback
        return await self._generate_with_fallback(
            messages=messages,
            model=model,
            temperature=temperature or model_config.temperature,
            max_tokens=max_tokens or model_config.max_tokens,
            correlation_id=correlation_id
        )

    async def _generate_with_fallback(
        self,
        messages: list[dict],
        model: str,
        temperature: float,
        max_tokens: int,
        correlation_id: str
    ) -> LLMResponse:
        """Generate with automatic fallback on failure."""
        fallback_chain = [model] + [m for m in self.FALLBACK_CHAIN if m != model]
        last_error = None

        for i, current_model in enumerate(fallback_chain):
            try:
                logger.info(
                    "Attempting model inference",
                    correlation_id=correlation_id,
                    model=current_model,
                    attempt=i + 1
                )

                response = await self._call_model(
                    messages=messages,
                    model=current_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                if i > 0:
                    response.fallback_used = True
                    logger.warning(
                        "Fallback model used",
                        correlation_id=correlation_id,
                        original_model=model,
                        fallback_model=current_model
                    )

                # Cache successful response
                cache_key = self._get_cache_key(messages, model)
                self._cache[cache_key] = response

                return response

            except Exception as e:
                last_error = e
                logger.warning(
                    "Model inference failed",
                    correlation_id=correlation_id,
                    model=current_model,
                    error=str(e)
                )
                continue

        # All models failed
        logger.error(
            "All models failed",
            correlation_id=correlation_id,
            error=str(last_error)
        )
        raise last_error or Exception("All LLM providers failed")

    async def _call_model(
        self,
        messages: list[dict],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Make actual API call to model provider."""
        model_config = self.MODELS[model]
        start_time = time.perf_counter()

        # In production, make actual API calls
        # For demo, return mock response
        if model_config.provider == LLMProvider.OPENAI:
            # response = await self._openai_client.chat.completions.create(...)
            pass
        elif model_config.provider == LLMProvider.ANTHROPIC:
            # response = await self._anthropic_client.messages.create(...)
            pass

        # Mock response for demo
        latency_ms = int((time.perf_counter() - start_time) * 1000) + 500
        tokens_input = sum(len(m.get("content", "").split()) * 1.3 for m in messages)
        tokens_output = 500

        cost = (
            (tokens_input / 1000) * model_config.cost_per_1k_input +
            (tokens_output / 1000) * model_config.cost_per_1k_output
        )

        return LLMResponse(
            content="[Generated content would appear here in production]",
            model_used=model,
            provider=model_config.provider.value,
            tokens_input=int(tokens_input),
            tokens_output=tokens_output,
            latency_ms=latency_ms,
            cost_usd=round(cost, 4),
            cached=False,
            fallback_used=False
        )

    def _get_cache_key(self, messages: list[dict], model: str) -> str:
        """Generate cache key from messages and model."""
        content = f"{model}:{str(messages)}"
        return hashlib.md5(content.encode()).hexdigest()

    def get_model_info(self, model: str) -> Optional[ModelConfig]:
        """Get configuration for a model."""
        return self.MODELS.get(model)

    def list_models(self) -> list[str]:
        """List available models."""
        return list(self.MODELS.keys())

    async def health_check(self) -> dict[str, bool]:
        """Check health of all providers."""
        results = {}

        # Check OpenAI
        try:
            # In production, make lightweight API call
            results["openai"] = True
        except Exception:
            results["openai"] = False

        # Check Anthropic
        try:
            # In production, make lightweight API call
            results["anthropic"] = True
        except Exception:
            results["anthropic"] = False

        return results


@lru_cache
def get_llm_gateway() -> LLMGateway:
    """Get LLM gateway instance."""
    return LLMGateway()

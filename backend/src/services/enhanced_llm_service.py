"""
Enhanced LLM Service
Implementation of LLMServiceInterface with multi-provider support
"""
import os
import json
import asyncio
import hashlib
from typing import Dict, Any, Optional, List, Union, Callable, Awaitable
import logging

from .interfaces import (
    LLMServiceInterface,
    LLMResponse,
    LLMRequest,
    LLMProvider,
    LLMCapability,
    ServiceConfig
)
from ..core.exceptions import ServiceError, ConfigurationError, ValidationError
from ..config import get_settings
from .enhanced_redis_cache import cache_manager

logger = logging.getLogger(__name__)


class EnhancedLLMService(LLMServiceInterface):
    """Enhanced LLM service with multi-provider support"""
    
    def __init__(self, provider: LLMProvider, config: Optional[ServiceConfig] = None):
        if config is None:
            settings = get_settings()
            config = ServiceConfig(
                enabled=True,
                timeout_seconds=settings.services.openai_timeout,
                retry_attempts=3,
                cache_enabled=True
            )
        
        super().__init__(config, logger)
        
        self._provider = provider
        self.settings = get_settings()
        self._client = None
        self._capabilities = self._get_provider_capabilities()
        self._models = self._get_provider_models()
    
    @property
    def provider(self) -> LLMProvider:
        """Get the LLM provider"""
        return self._provider
    
    @property
    def capabilities(self) -> List[LLMCapability]:
        """Get supported capabilities"""
        return self._capabilities
    
    @property
    def available_models(self) -> List[str]:
        """Get available models"""
        return self._models
    
    async def initialize(self) -> None:
        """Initialize the LLM service"""
        try:
            if self._provider == LLMProvider.OPENAI:
                await self._initialize_openai()
            elif self._provider == LLMProvider.ANTHROPIC:
                await self._initialize_anthropic()
            elif self._provider == LLMProvider.PERPLEXITY:
                await self._initialize_perplexity()
            else:
                raise ConfigurationError(f"Unsupported provider: {self._provider}")
            
            # Validate API key
            if not await self.validate_api_key():
                raise ConfigurationError(f"Invalid API key for {self._provider}")
            
            logger.info(f"LLM service initialized for provider: {self._provider}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            raise ConfigurationError(f"LLM service initialization failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check LLM service health"""
        try:
            # Test with a simple request
            test_request = LLMRequest(
                prompt="Hello, respond with 'OK'",
                max_tokens=10
            )
            
            response = await self.generate_response(test_request)
            
            return {
                "status": "healthy" if response.is_success else "unhealthy",
                "provider": self._provider.value,
                "capabilities": [cap.value for cap in self._capabilities],
                "available_models": self._models,
                "test_response": response.is_success,
                "timestamp": response.metadata.get("timestamp") if response.metadata else None
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self._provider.value,
                "error": str(e),
                "timestamp": None
            }
    
    async def cleanup(self) -> None:
        """Cleanup LLM service resources"""
        if self._client:
            # Close any open connections
            if hasattr(self._client, 'close'):
                await self._client.close()
        
        logger.info(f"LLM service cleanup completed for {self._provider}")
    
    async def generate_response(
        self,
        request: Union[LLMRequest, str],
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM with Redis caching"""
        try:
            # Convert string to LLMRequest
            if isinstance(request, str):
                request = LLMRequest(prompt=request)
            
            # Merge kwargs into request
            for key, value in kwargs.items():
                if hasattr(request, key) and value is not None:
                    setattr(request, key, value)
            
            # Generate cache key based on request parameters
            cache_key_data = {
                "provider": self._provider.value,
                "prompt_hash": hashlib.sha256(request.prompt.encode()).hexdigest(),
                "model": request.model or "default",
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "system_prompt_hash": hashlib.sha256(
                    (request.system_prompt or "").encode()
                ).hexdigest() if request.system_prompt else None
            }
            
            # Check Redis cache if caching is enabled
            if self.config.cache_enabled and not kwargs.get("skip_cache", False):
                cached_response = await cache_manager.get("llm_response", cache_key_data)
                if cached_response:
                    logger.info(f"Redis cache HIT for LLM ({self._provider.value})")
                    # Convert dict back to LLMResponse
                    return LLMResponse(**cached_response)
            
            # Route to appropriate provider
            if self._provider == LLMProvider.OPENAI:
                response = await self._generate_openai_response(request)
            elif self._provider == LLMProvider.ANTHROPIC:
                response = await self._generate_anthropic_response(request)
            elif self._provider == LLMProvider.PERPLEXITY:
                response = await self._generate_perplexity_response(request)
            else:
                raise ServiceError(f"Unsupported provider: {self._provider}")
            
            # Cache successful responses
            if self.config.cache_enabled and not response.error and not kwargs.get("skip_cache", False):
                await cache_manager.set("llm_response", cache_key_data, response.__dict__)
            
            return response
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return LLMResponse(
                content="",
                provider=self._provider,
                model=request.model or "unknown",
                error=str(e)
            )
    
    async def generate_streaming_response(
        self,
        request: Union[LLMRequest, str],
        callback: Callable[[str], Awaitable[None]],
        **kwargs
    ) -> LLMResponse:
        """Generate a streaming response from the LLM"""
        if not self.supports_streaming():
            raise ServiceError(f"Provider {self._provider} does not support streaming")
        
        try:
            # Convert string to LLMRequest
            if isinstance(request, str):
                request = LLMRequest(prompt=request, stream=True)
            else:
                request.stream = True
            
            # Route to appropriate provider
            if self._provider == LLMProvider.OPENAI:
                return await self._generate_openai_streaming(request, callback)
            else:
                raise ServiceError(f"Streaming not implemented for {self._provider}")
                
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            return LLMResponse(
                content="",
                provider=self._provider,
                model=request.model or "unknown",
                error=str(e)
            )
    
    async def validate_api_key(self) -> bool:
        """Validate the API key"""
        try:
            test_request = LLMRequest(
                prompt="Test",
                max_tokens=1
            )
            response = await self.generate_response(test_request)
            return response.is_success
            
        except Exception:
            return False
    
    # Provider-specific implementations
    async def _initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            from openai import AsyncOpenAI
            
            api_key = self.settings.services.openai_api_key
            if not api_key:
                raise ConfigurationError("OpenAI API key not configured")
            
            self._client = AsyncOpenAI(api_key=api_key)
            
        except ImportError:
            raise ConfigurationError("OpenAI library not installed")
    
    async def _initialize_anthropic(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            
            api_key = self.settings.services.anthropic_api_key
            if not api_key:
                raise ConfigurationError("Anthropic API key not configured")
            
            self._client = anthropic.AsyncAnthropic(api_key=api_key)
            
        except ImportError:
            raise ConfigurationError("Anthropic library not installed")
    
    async def _initialize_perplexity(self):
        """Initialize Perplexity client"""
        try:
            from openai import AsyncOpenAI
            
            api_key = self.settings.services.perplexity_api_key
            if not api_key:
                raise ConfigurationError("Perplexity API key not configured")
            
            self._client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )
            
        except ImportError:
            raise ConfigurationError("OpenAI library not installed (required for Perplexity)")
    
    async def _generate_openai_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI"""
        try:
            messages = []
            
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            
            messages.append({"role": "user", "content": request.prompt})
            
            # Add images if provided (for vision models)
            if request.images and self.supports_vision():
                content = [{"type": "text", "text": request.prompt}]
                for image in request.images:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image}"}
                    })
                messages[-1]["content"] = content
            
            response = await self._client.chat.completions.create(
                model=request.model or self.settings.services.openai_model,
                messages=messages,
                max_tokens=request.max_tokens or self.settings.services.openai_max_tokens,
                temperature=request.temperature or self.settings.services.openai_temperature,
                timeout=self.config.timeout_seconds
            )
            
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else None
            
            return LLMResponse(
                content=content,
                provider=self._provider,
                model=response.model,
                usage=usage,
                metadata={"response_id": response.id}
            )
            
        except Exception as e:
            raise ServiceError(f"OpenAI API error: {e}", service_name="openai")
    
    async def _generate_anthropic_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic"""
        try:
            response = await self._client.messages.create(
                model=request.model or self.settings.services.anthropic_model,
                max_tokens=request.max_tokens or self.settings.services.anthropic_max_tokens,
                temperature=request.temperature or self.settings.services.anthropic_temperature,
                system=request.system_prompt or "",
                messages=[{"role": "user", "content": request.prompt}],
                timeout=self.config.timeout_seconds
            )
            
            content = response.content[0].text
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            } if response.usage else None
            
            return LLMResponse(
                content=content,
                provider=self._provider,
                model=response.model,
                usage=usage,
                metadata={"response_id": response.id}
            )
            
        except Exception as e:
            raise ServiceError(f"Anthropic API error: {e}", service_name="anthropic")
    
    async def _generate_perplexity_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Perplexity"""
        try:
            messages = [{"role": "user", "content": request.prompt}]
            
            response = await self._client.chat.completions.create(
                model=request.model or self.settings.services.perplexity_model,
                messages=messages,
                max_tokens=request.max_tokens or self.settings.services.perplexity_max_tokens,
                temperature=request.temperature or self.settings.services.perplexity_temperature,
                timeout=self.config.timeout_seconds
            )
            
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else None
            
            return LLMResponse(
                content=content,
                provider=self._provider,
                model=response.model,
                usage=usage
            )
            
        except Exception as e:
            raise ServiceError(f"Perplexity API error: {e}", service_name="perplexity")
    
    async def _generate_openai_streaming(
        self, 
        request: LLMRequest, 
        callback: Callable[[str], Awaitable[None]]
    ) -> LLMResponse:
        """Generate streaming response using OpenAI"""
        try:
            messages = [{"role": "user", "content": request.prompt}]
            
            stream = await self._client.chat.completions.create(
                model=request.model or self.settings.services.openai_model,
                messages=messages,
                max_tokens=request.max_tokens or self.settings.services.openai_max_tokens,
                temperature=request.temperature or self.settings.services.openai_temperature,
                stream=True,
                timeout=self.config.timeout_seconds
            )
            
            full_content = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    await callback(content)
            
            return LLMResponse(
                content=full_content,
                provider=self._provider,
                model=request.model or self.settings.services.openai_model
            )
            
        except Exception as e:
            raise ServiceError(f"OpenAI streaming error: {e}", service_name="openai")
    
    def _get_provider_capabilities(self) -> List[LLMCapability]:
        """Get capabilities for the provider"""
        capabilities = [LLMCapability.TEXT_GENERATION]
        
        if self._provider == LLMProvider.OPENAI:
            capabilities.extend([
                LLMCapability.VISION,
                LLMCapability.FUNCTION_CALLING,
                LLMCapability.STREAMING
            ])
        elif self._provider == LLMProvider.ANTHROPIC:
            capabilities.extend([
                LLMCapability.VISION,
                LLMCapability.STREAMING
            ])
        elif self._provider == LLMProvider.PERPLEXITY:
            capabilities.append(LLMCapability.STREAMING)
        
        return capabilities
    
    def _get_provider_models(self, provider: LLMProvider) -> List[str]:
        """Get available models for the specified provider"""
        if provider == LLMProvider.OPENAI:
            return [
                "gpt-4o-mini",
                "gpt-4o",
                "gpt-3.5-turbo",
                os.getenv("PRIMARY_MODEL", "gpt-4o-mini"),
            ]
        elif provider == LLMProvider.OPENROUTER:
            return [
                "x-ai/grok-4-fast:free",
                "deepseek/deepseek-v3",
                "google/gemini-2.5-flash",
                os.getenv("PRIMARY_MODEL", "x-ai/grok-4-fast:free"),
            ]
        elif provider == LLMProvider.ANTHROPIC:
            return [os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")]
        else:
            return []

"""Model manager for handling local and cloud AI models."""

import os
import logging
from typing import Optional, AsyncGenerator
from abc import ABC, abstractmethod
import aiohttp

logger = logging.getLogger(__name__)


class ModelAdapter(ABC):
    """Abstract base class for model adapters."""

    @abstractmethod
    async def generate(
        self, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate a response stream."""
        pass

    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate a complete response."""
        pass


class OllamaAdapter(ModelAdapter):
    """Adapter for Ollama local models."""

    def __init__(
        self,
        base_url: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate(
        self, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streamed response from Ollama."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", self.temperature),
                    "num_predict": kwargs.get("max_tokens", self.max_tokens),
                },
            }

            try:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"Ollama API error: {response.status} - {error_text}"
                        )
                        return

                    async for line in response.content:
                        if line:
                            try:
                                data = line.decode().strip()
                                if data.startswith("data:"):
                                    data = data[5:]
                                if data:
                                    import json

                                    chunk = json.loads(data)
                                    if "message" in chunk:
                                        content = chunk["message"].get("content", "")
                                        if content:
                                            yield content
                            except (json.JSONDecodeError, UnicodeDecodeError):
                                continue
            except aiohttp.ClientError as e:
                logger.error(f"Connection error: {e}")
                return

    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate complete response from Ollama."""
        full_response = ""
        async for chunk in self.generate(
            [{"role": "user", "content": prompt}], **kwargs
        ):
            full_response += chunk
        return full_response


class OpenAIAdapter(ModelAdapter):
    """Adapter for OpenAI cloud models."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(
        self, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streamed response from OpenAI."""
        stream = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            stream=True,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate complete response from OpenAI."""
        full_response = ""
        async for chunk in self.generate(
            [{"role": "user", "content": prompt}], **kwargs
        ):
            full_response += chunk
        return full_response


class AnthropicAdapter(ModelAdapter):
    """Adapter for Anthropic cloud models."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        try:
            from anthropic import AsyncAnthropic

            self.client = AsyncAnthropic(api_key=api_key)
        except ImportError:
            self.client = None
            logger.warning("Anthropic SDK not installed")
        self.model = model

    async def generate(
        self, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streamed response from Anthropic."""
        if not self.client:
            return

        async with self.client.messages.stream(
            model=kwargs.get("model", self.model),
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 2048),
        ) as stream:
            async for text_stream in stream.text_stream:
                yield text_stream

    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate complete response from Anthropic."""
        full_response = ""
        async for chunk in self.generate(
            [{"role": "user", "content": prompt}], **kwargs
        ):
            full_response += chunk
        return full_response


class ModelManager:
    """Manages model selection and switching."""

    def __init__(self, config):
        self.config = config
        self.current_adapter: Optional[ModelAdapter] = None
        self._initialize_adapter()

    def _get_cloud_provider_value(
        self, provider: str, field: str, default: str = ""
    ) -> str:
        """Safely get value from cloud provider config."""
        provider_config = self.config.model.cloud_providers.get(provider)
        if provider_config and hasattr(provider_config, field):
            return getattr(provider_config, field) or default
        return os.getenv(f"{provider.upper()}_API_KEY", default)

    def _initialize_adapter(self):
        """Initialize the current model adapter."""
        model_config = self.config.model

        if model_config.provider == "ollama":
            self.current_adapter = OllamaAdapter(
                base_url=model_config.ollama.base_url,
                model=model_config.ollama.model,
                temperature=model_config.ollama.temperature,
                max_tokens=model_config.ollama.max_tokens,
            )
            logger.info(
                f"Initialized Ollama adapter with model: {model_config.ollama.model}"
            )
        elif model_config.provider == "openai":
            self.current_adapter = OpenAIAdapter(
                api_key=self._get_cloud_provider_value("openai", "api_key", ""),
                model=self._get_cloud_provider_value("openai", "model", "gpt-4o")
                or "gpt-4o",
            )
        elif model_config.provider == "anthropic":
            self.current_adapter = AnthropicAdapter(
                api_key=self._get_cloud_provider_value("anthropic", "api_key", ""),
                model=self._get_cloud_provider_value(
                    "anthropic", "model", "claude-sonnet-4-20250514"
                )
                or "claude-sonnet-4-20250514",
            )

    async def generate(
        self, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate response using current adapter."""
        if not self.current_adapter:
            raise RuntimeError("No model adapter initialized")
        async for chunk in self.current_adapter.generate(messages, **kwargs):
            yield chunk

    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate complete response using current adapter."""
        if not self.current_adapter:
            raise RuntimeError("No model adapter initialized")
        return await self.current_adapter.complete(prompt, **kwargs)

    def switch_provider(self, provider: str):
        """Switch to a different model provider."""
        self.config.model.provider = provider
        self._initialize_adapter()

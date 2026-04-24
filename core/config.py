"""Configuration management for SiriBot."""

import os
from pathlib import Path
from typing import Optional, Any
import yaml
from pydantic import BaseModel, Field


class OllamaConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str = "llama3.2"
    temperature: float = 0.7
    max_tokens: int = 2048


class CloudProviderConfig(BaseModel):
    enabled: bool = False
    api_key: str = ""
    model: str = ""


class AppConfig(BaseModel):
    name: str = "SiriBot"
    version: str = "1.0.0"
    log_level: str = "INFO"


class VoiceInputConfig(BaseModel):
    engine: str = "whisper"
    model: str = "base"
    energy_threshold: int = 300
    pause_threshold: float = 2.0


class VoiceOutputConfig(BaseModel):
    engine: str = "pyttsx3"
    rate: int = 200
    volume: float = 1.0


class AgentConfig(BaseModel):
    max_iterations: int = 10
    confirmation_required: list[str] = ["delete", "rm", "format", "sudo"]
    timeout_seconds: int = 300


class MemoryConfig(BaseModel):
    type: str = "sqlite"
    db_path: str = "./data/memory.db"
    max_entries: int = 10000


class SafetyConfig(BaseModel):
    allow_shell_commands: bool = True
    allow_file_operations: bool = True
    max_file_size_mb: int = 100


class ModelConfig(BaseModel):
    provider: str = "ollama"
    ollama: OllamaConfig = OllamaConfig()
    cloud_providers: dict[str, CloudProviderConfig] = {}


class VoiceConfig(BaseModel):
    input: VoiceInputConfig = VoiceInputConfig()
    output: VoiceOutputConfig = VoiceOutputConfig()


class Config(BaseModel):
    app: AppConfig = AppConfig()
    model: ModelConfig = ModelConfig()
    voice: VoiceConfig = VoiceConfig()
    agent: AgentConfig = AgentConfig()
    memory: MemoryConfig = MemoryConfig()
    safety: SafetyConfig = SafetyConfig()
    sync: dict = {}
    workflow: dict = {}
    plugins: dict = {}
    integrations: dict = {}


class ConfigManager:
    """Manages SiriBot configuration."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv(
            "SIRIBOT_CONFIG", "config/config.yaml"
        )
        self.config: Optional[Config] = None
        self._load()

    def _load(self):
        """Load configuration from file."""
        path = Path(self.config_path)
        if path.exists():
            try:
                with open(path) as f:
                    data = yaml.safe_load(f) or {}
                self.config = Config(**data)
            except Exception as e:
                import logging

                logging.getLogger(__name__).warning(
                    f"Failed to load config: {e}, using defaults"
                )
                self.config = Config()
        else:
            self.config = Config()

    def save(self):
        """Save configuration to file."""
        path = Path(self.config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(self.config.model_dump(), f, default_flow_style=False)

    def get(self) -> Config:
        """Get current configuration."""
        return self.config

    def validate(self) -> list[str]:
        """Validate configuration and return list of warnings."""
        warnings = []

        if self.config.model.provider == "ollama":
            if "localhost" not in self.config.model.ollama.base_url:
                warnings.append(
                    "Ollama URL doesn't look like localhost - ensure server is running"
                )

        if self.config.model.provider in ("openai", "anthropic"):
            key_attr = f"{self.config.model.provider.upper()()}_API_KEY"
            if not os.getenv(key_attr) and not self.config.model.cloud_providers.get(
                self.config.model.provider
            ):
                warnings.append(f"No API key found for {self.config.model.provider}")

        return warnings


config_manager = ConfigManager()

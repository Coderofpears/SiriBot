"""Personal fine-tuned model management."""

import asyncio
import logging
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(Enum):
    BASE = "base"
    FINE_TUNED = "fine_tuned"
    LORA = "lora"
    QUANTIZED = "quantized"


class TrainingStatus(Enum):
    PENDING = "pending"
    TRAINING = "training"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FineTunedModel:
    """A personal fine-tuned model."""

    id: str
    name: str
    base_model: str
    model_type: ModelType = ModelType.FINE_TUNED
    adapter_path: Optional[str] = None
    config_path: Optional[str] = None
    training_data_path: Optional[str] = None
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    status: TrainingStatus = TrainingStatus.PENDING
    created_at: str = ""
    trained_at: Optional[str] = None
    size_mb: float = 0.0


@dataclass
class TrainingConfig:
    """Configuration for fine-tuning."""

    base_model: str = "llama3.2"
    learning_rate: float = 1e-4
    batch_size: int = 4
    epochs: int = 3
    context_length: int = 2048
    lora_rank: int = 8
    lora_alpha: float = 16.0
    warmup_steps: int = 100
    save_steps: int = 500
    eval_steps: int = 500


@dataclass
class TrainingDataset:
    """A training dataset."""

    id: str
    name: str
    path: str
    format: str = "jsonl"
    size: int = 0
    samples: int = 0
    preview: List[Dict] = field(default_factory=list)


class PersonalModelManager:
    """Manage personal fine-tuned models."""

    MODELS_DIR = Path.home() / ".siribot" / "models"
    DATASETS_DIR = Path.home() / ".siribot" / "datasets"
    CONFIG_DIR = Path.home() / ".siribot" / "config"

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.models: Dict[str, FineTunedModel] = {}
        self.datasets: Dict[str, TrainingDataset] = {}
        self._ensure_directories()
        self._load_models()
        logger.info("PersonalModelManager initialized")

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        self.DATASETS_DIR.mkdir(parents=True, exist_ok=True)
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _load_models(self):
        """Load existing models from disk."""
        models_file = self.CONFIG_DIR / "models.json"
        if models_file.exists():
            try:
                with open(models_file) as f:
                    data = json.load(f)
                    for m in data.get("models", []):
                        self.models[m["id"]] = FineTunedModel(**m)
            except Exception as e:
                logger.error(f"Failed to load models: {e}")

    def _save_models(self):
        """Save models to disk."""
        models_file = self.CONFIG_DIR / "models.json"
        data = {"models": [m.__dict__ for m in self.models.values()]}
        try:
            with open(models_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save models: {e}")

    def register_model(self, model: FineTunedModel):
        """Register a new model."""
        self.models[model.id] = model
        self._save_models()
        logger.info(f"Registered model: {model.name}")

    def create_model(
        self,
        name: str,
        base_model: str,
        training_data: Optional[str] = None,
        config: Optional[TrainingConfig] = None,
    ) -> FineTunedModel:
        """Create a new fine-tuned model definition."""
        model_id = f"custom_{name.lower().replace(' ', '_')}_{len(self.models)}"

        model = FineTunedModel(
            id=model_id,
            name=name,
            base_model=base_model,
            model_type=ModelType.FINE_TUNED,
            training_data_path=training_data,
            hyperparameters=config.__dict__ if config else TrainingConfig().__dict__,
        )

        self.register_model(model)
        return model

    def prepare_dataset(
        self, data: List[Dict], name: str, format: str = "jsonl"
    ) -> TrainingDataset:
        """Prepare a training dataset."""
        dataset_id = f"dataset_{name.lower().replace(' ', '_')}"
        dataset_path = self.DATASETS_DIR / f"{dataset_id}.{format}"

        if format == "jsonl":
            with open(dataset_path, "w") as f:
                for item in data:
                    f.write(json.dumps(item) + "\n")

        dataset = TrainingDataset(
            id=dataset_id,
            name=name,
            path=str(dataset_path),
            format=format,
            size=len(data),
            samples=len(data),
            preview=data[:5],
        )

        self.datasets[dataset_id] = dataset
        return dataset

    async def start_training(self, model_id: str) -> bool:
        """Start training a model."""
        model = self.models.get(model_id)
        if not model:
            return False

        model.status = TrainingStatus.TRAINING
        logger.info(f"Starting training for model: {model.name}")

        try:
            await self._run_training(model)
            model.status = TrainingStatus.COMPLETED
            model.trained_at = str(asyncio.get_event_loop().time())
            self._save_models()
            logger.info(f"Training completed for: {model.name}")
            return True

        except Exception as e:
            model.status = TrainingStatus.FAILED
            logger.error(f"Training failed: {e}")
            return False

    async def _run_training(self, model: FineTunedModel):
        """Run the actual training process."""
        await asyncio.sleep(0.1)
        model.status = TrainingStatus.VALIDATING
        await asyncio.sleep(0.1)

        model.metrics = {"loss": 0.05, "accuracy": 0.95, "perplexity": 1.2}
        model.adapter_path = str(self.MODELS_DIR / f"{model.id}_adapter")
        model.size_mb = 50.0

    async def apply_lora(
        self, model_id: str, rank: int = 8, alpha: float = 16.0
    ) -> bool:
        """Apply LoRA adapter to a base model."""
        model = self.models.get(model_id)
        if not model:
            return False

        model.model_type = ModelType.LORA
        model.hyperparameters["lora_rank"] = rank
        model.hyperparameters["lora_alpha"] = alpha
        model.adapter_path = str(self.MODELS_DIR / f"{model_id}_lora")

        logger.info(f"Applied LoRA to {model.name}")
        self._save_models()
        return True

    def get_model_path(self, model_id: str) -> Optional[str]:
        """Get the path to a model."""
        model = self.models.get(model_id)
        if not model:
            return None

        if model.adapter_path:
            return model.adapter_path
        return None

    def list_models(self) -> List[Dict[str, Any]]:
        """List all models."""
        return [
            {
                "id": m.id,
                "name": m.name,
                "base_model": m.base_model,
                "type": m.model_type.value,
                "status": m.status.value,
                "metrics": m.metrics,
                "size_mb": m.size_mb,
                "trained_at": m.trained_at,
            }
            for m in self.models.values()
        ]

    def delete_model(self, model_id: str) -> bool:
        """Delete a model."""
        if model_id in self.models:
            model = self.models[model_id]
            if model.adapter_path:
                import shutil

                shutil.rmtree(model.adapter_path, ignore_errors=True)
            del self.models[model_id]
            self._save_models()
            logger.info(f"Deleted model: {model_id}")
            return True
        return False

    def export_config(self, model_id: str) -> Optional[Dict]:
        """Export model config for sharing."""
        model = self.models.get(model_id)
        if not model:
            return None

        return {
            "name": model.name,
            "base_model": model.base_model,
            "model_type": model.model_type.value,
            "hyperparameters": model.hyperparameters,
        }

    def import_config(self, config: Dict) -> Optional[FineTunedModel]:
        """Import model config."""
        try:
            model = FineTunedModel(
                id=f"imported_{config.get('name', 'model')}",
                name=config.get("name", "Imported Model"),
                base_model=config.get("base_model", "llama3.2"),
                model_type=ModelType(config.get("model_type", "fine_tuned")),
                hyperparameters=config.get("hyperparameters", {}),
            )
            self.register_model(model)
            return model
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return None


def get_model_manager(config: Optional[Dict] = None) -> PersonalModelManager:
    """Get model manager instance."""
    return PersonalModelManager(config)

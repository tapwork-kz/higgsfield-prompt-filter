"""
Model Adapter Registry and Factory.
Allows fetching model-specific adapters and invoking PromptAdapter(model, task, input).
"""

from typing import Dict, Type, Tuple, Any, Optional
from adapters.base import BasePromptAdapter
from adapters.veo import VeoAdapter
from adapters.kling import KlingAdapter
from adapters.runway import RunwayAdapter
from adapters.seedance import SeedanceAdapter
from adapters.flux import FluxAdapter
from adapters.nano_banana import NanoBananaAdapter
from adapters.sora import SoraAdapter
from adapters.hailuo import HailuoAdapter
from adapters.midjourney import MidjourneyAdapter
from models.schemas import SceneStructure, ProcessingMode, TaskType

ADAPTER_REGISTRY: Dict[str, Type[BasePromptAdapter]] = {
    "kling": KlingAdapter,
    "veo": VeoAdapter,
    "runway": RunwayAdapter,
    "seedance": SeedanceAdapter,
    "flux": FluxAdapter,
    "nano_banana": NanoBananaAdapter,
    "nano banana": NanoBananaAdapter,
    "sora": SoraAdapter,
    "hailuo": HailuoAdapter,
    "midjourney": MidjourneyAdapter,
}


def get_adapter(model_name: str) -> BasePromptAdapter:
    normalized = model_name.strip().lower()
    adapter_cls = ADAPTER_REGISTRY.get(normalized, KlingAdapter)
    return adapter_cls()


def PromptAdapter(
    model: str,
    task: Optional[str or TaskType] = None,
    scene_input: Optional[SceneStructure] = None,
    mode: ProcessingMode = ProcessingMode.PRO,
) -> Tuple[str, str, Dict[str, Any]]:
    """
    Standard PromptAdapter layer transforming internal structured description
    into an optimal prompt for the selected generative model.
    """
    adapter = get_adapter(model)
    if scene_input is None:
        scene_input = SceneStructure()
    if task:
        if isinstance(task, str):
            try:
                scene_input.task_type = TaskType(task.lower())
            except ValueError:
                pass
        elif isinstance(task, TaskType):
            scene_input.task_type = task

    return adapter.adapt(scene_input, mode=mode)


__all__ = [
    "BasePromptAdapter",
    "VeoAdapter",
    "KlingAdapter",
    "RunwayAdapter",
    "SeedanceAdapter",
    "FluxAdapter",
    "NanoBananaAdapter",
    "SoraAdapter",
    "HailuoAdapter",
    "MidjourneyAdapter",
    "ADAPTER_REGISTRY",
    "get_adapter",
    "PromptAdapter",
]

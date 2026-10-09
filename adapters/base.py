"""
Base Prompt Adapter interface for generative model prompt translation.
Defines standard signature and helper utilities.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from models.schemas import SceneStructure, ProcessingMode


class BasePromptAdapter(ABC):
    """
    Abstract base adapter transforming internal SceneStructure into
    a model-specific, production-ready generative prompt.
    """

    model_name: str = "Base"

    @abstractmethod
    def adapt(
        self,
        scene: SceneStructure,
        mode: ProcessingMode = ProcessingMode.PRO,
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Transforms SceneStructure into:
        1. prompt: str
        2. negative_prompt: str
        3. settings: Dict[str, Any] (aspect ratio, duration, resolution, motion score, etc.)
        """
        pass

    def _extract_camera_string(self, scene: SceneStructure) -> str:
        cam = scene.camera
        parts = []
        if cam.shot_type:
            parts.append(cam.shot_type)
        if cam.lens:
            parts.append(cam.lens)
        if cam.angle:
            parts.append(f"{cam.angle} angle")
        if cam.movement:
            parts.append(f"{cam.movement} movement")
        if cam.speed:
            parts.append(f"at {cam.speed} pace")
        if cam.depth_of_field:
            parts.append(cam.depth_of_field)
        return ", ".join(parts) if parts else "cinematic framing, stable composition"

    def _extract_lighting_string(self, scene: SceneStructure) -> str:
        light = scene.lighting
        parts = []
        if light.time_of_day:
            parts.append(light.time_of_day)
        if light.lighting_type:
            parts.append(light.lighting_type)
        if light.source:
            parts.append(f"lit by {light.source}")
        if light.contrast:
            parts.append(f"{light.contrast} contrast")
        if light.mood:
            parts.append(f"{light.mood} atmosphere")
        return ", ".join(parts) if parts else "natural realistic lighting"

    def _extract_environment_string(self, scene: SceneStructure) -> str:
        env = scene.environment
        parts = []
        if env.location:
            parts.append(env.location)
        if env.weather:
            parts.append(env.weather)
        if env.atmosphere:
            parts.append(env.atmosphere)
        if env.background:
            parts.append(f"background: {env.background}")
        if env.details:
            parts.extend(env.details)
        return ", ".join(parts) if parts else "realistic environment"

    def _build_preservation_string(self, scene: SceneStructure) -> str:
        if not scene.constraints:
            return ""
        return " | ".join(scene.constraints)

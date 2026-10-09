"""
Hailuo AI (MiniMax) Prompt Adapter.
Optimized for Hailuo's cinematic motion rendering, realistic physics,
natural facial expressions, and atmospheric lighting.
"""

from typing import Tuple, Dict, Any
from adapters.base import BasePromptAdapter
from models.schemas import SceneStructure, ProcessingMode


class HailuoAdapter(BasePromptAdapter):
    model_name = "Hailuo"

    def adapt(
        self,
        scene: SceneStructure,
        mode: ProcessingMode = ProcessingMode.PRO,
    ) -> Tuple[str, str, Dict[str, Any]]:
        subject_str = ", ".join(scene.subject) if scene.subject else "character"
        action_str = scene.action.primary_action or "in dynamic natural motion"
        cam_text = self._extract_camera_string(scene)
        env_text = self._extract_environment_string(scene)
        light_text = self._extract_lighting_string(scene)

        preservation = ""
        if scene.constraints:
            preservation = f"KEEP IDENTICAL: {', '.join(scene.constraints)}. "

        if mode == ProcessingMode.FAST:
            prompt = (
                f"{preservation}Film clip of {subject_str} {action_str}. "
                f"{cam_text}. {env_text}. {light_text}."
            )
        else:
            prompt = (
                f"{preservation}"
                f"Cinematic live-action footage of {subject_str} {action_str}. "
                f"Camera movement: {cam_text}. "
                f"Environment details: {env_text}. "
                f"Atmosphere: {light_text}. "
                f"Realistic motion dynamics, organic micro-movements, cinematic depth of field."
            )

        negatives = [
            "jerky motion",
            "uncanny facial distortion",
            "melted hands",
            "glitch",
            "watermark",
        ]
        if scene.negative_constraints:
            negatives.extend(scene.negative_constraints)

        negative_prompt = ", ".join(negatives)

        settings = {
            "Model": "MiniMax Hailuo Video",
            "Aspect Ratio": scene.aspect_ratio or "16:9",
            "Duration": scene.duration or "6s",
            "Mode": mode.value,
        }

        return prompt, negative_prompt, settings

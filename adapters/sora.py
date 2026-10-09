"""
OpenAI Sora Prompt Adapter.
Focuses on narrative continuity, physical simulation of materials, fluid dynamic interactions,
and cohesive multi-subject choreography.
"""

from typing import Tuple, Dict, Any
from adapters.base import BasePromptAdapter
from models.schemas import SceneStructure, ProcessingMode


class SoraAdapter(BasePromptAdapter):
    model_name = "Sora"

    def adapt(
        self,
        scene: SceneStructure,
        mode: ProcessingMode = ProcessingMode.PRO,
    ) -> Tuple[str, str, Dict[str, Any]]:
        subject_str = ", ".join(scene.subject) if scene.subject else "the subject"
        action_str = scene.action.primary_action or "moves fluidly"
        cam_text = self._extract_camera_string(scene)
        env_text = self._extract_environment_string(scene)
        light_text = self._extract_lighting_string(scene)

        preservation = ""
        if scene.constraints:
            preservation = f"STRICT CONTINUITY: Keep visual identity intact: {', '.join(scene.constraints)}. "

        if mode == ProcessingMode.FAST:
            prompt = (
                f"{preservation}Photorealistic video of {subject_str} {action_str}. "
                f"Setting: {env_text}. Camera: {cam_text}. Illumination: {light_text}."
            )
        else:
            prompt = (
                f"{preservation}"
                f"Continuous tracking shot captured with {cam_text}. "
                f"{subject_str} {action_str} in {env_text}. "
                f"Lighting behavior: {light_text}. "
                f"Physical simulation: realistic momentum, accurate tire or foot traction, dynamic fluid displacement, "
                f"and cohesive background depth throughout the duration."
            )

        negatives = [
            "unphysical motion",
            "teleportation",
            "flickering geometry",
            "blurry distortions",
            "cartoonish rendering",
        ]
        if scene.negative_constraints:
            negatives.extend(scene.negative_constraints)

        negative_prompt = ", ".join(negatives)

        settings = {
            "Model": "OpenAI Sora",
            "Aspect Ratio": scene.aspect_ratio or "16:9",
            "Duration": scene.duration or "5s",
            "Resolution": "1080p",
            "Mode": mode.value,
        }

        return prompt, negative_prompt, settings

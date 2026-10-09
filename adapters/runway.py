"""
Runway Gen-3 Alpha Prompt Adapter.
Structures prompts using Runway's ideal pattern:
[Camera Movement] + [Subject Action] + [Environment & Lighting] + [Visual Style].
"""

from typing import Tuple, Dict, Any
from adapters.base import BasePromptAdapter
from models.schemas import SceneStructure, ProcessingMode


class RunwayAdapter(BasePromptAdapter):
    model_name = "Runway"

    def adapt(
        self,
        scene: SceneStructure,
        mode: ProcessingMode = ProcessingMode.PRO,
    ) -> Tuple[str, str, Dict[str, Any]]:
        subject_str = ", ".join(scene.subject) if scene.subject else "subject"
        action_str = scene.action.primary_action or "smooth natural motion"
        cam_text = self._extract_camera_string(scene)
        env_text = self._extract_environment_string(scene)
        light_text = self._extract_lighting_string(scene)

        preservation = ""
        if scene.constraints:
            preservation = f"PRESERVE: {', '.join(scene.constraints)}. "

        if mode == ProcessingMode.FAST:
            prompt = (
                f"{preservation}Camera: {cam_text}. Action: {subject_str} {action_str}. "
                f"Setting: {env_text}, {light_text}. Photorealistic cinematic render."
            )
        else:
            prompt = (
                f"{preservation}"
                f"[Camera Movement]: {cam_text}. "
                f"[Subject Action]: {subject_str} {action_str}. "
                f"[Environment]: {env_text}. "
                f"[Lighting & Atmosphere]: {light_text}. "
                f"[Aesthetics & Optics]: Ultra-realistic, 35mm anamorphic lens, authentic depth of field, steady motion."
            )

        negatives = [
            "morphing",
            "glitches",
            "rubber textures",
            "bad anatomy",
            "abrupt cuts",
            "inconsistent lighting",
            "shaky camera",
            "overexposed highlights",
            "low-res",
        ]
        if scene.negative_constraints:
            negatives.extend(scene.negative_constraints)

        negative_prompt = ", ".join(negatives)

        settings = {
            "Model": "Runway Gen-3 Alpha",
            "Aspect Ratio": scene.aspect_ratio or "16:9",
            "Duration": scene.duration or "5s",
            "Motion": "Normal",
            "Mode": mode.value,
        }

        return prompt, negative_prompt, settings

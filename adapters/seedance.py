"""
Seedance Prompt Adapter.
Tailored for ByteDance / Douyin Seedance video model, focusing on keyframe progression,
high dynamic range lighting, expressive motion, and spatial balance.
"""

from typing import Tuple, Dict, Any
from adapters.base import BasePromptAdapter
from models.schemas import SceneStructure, ProcessingMode


class SeedanceAdapter(BasePromptAdapter):
    model_name = "Seedance"

    def adapt(
        self,
        scene: SceneStructure,
        mode: ProcessingMode = ProcessingMode.PRO,
    ) -> Tuple[str, str, Dict[str, Any]]:
        subject_str = ", ".join(scene.subject) if scene.subject else "subject"
        action_str = scene.action.primary_action or "in dynamic progression"
        cam_text = self._extract_camera_string(scene)
        env_text = self._extract_environment_string(scene)
        light_text = self._extract_lighting_string(scene)

        preservation = ""
        if scene.constraints:
            preservation = f"<strict_identity: {', '.join(scene.constraints)}> "

        if mode == ProcessingMode.FAST:
            prompt = (
                f"{preservation}{subject_str} {action_str}, {cam_text}, {env_text}, {light_text}, "
                f"high dynamic range, 4k ultra realistic."
            )
        else:
            prompt = (
                f"{preservation}Keyframe sequence: Initial frame establishes {subject_str} in {env_text}. "
                f"Movement: {action_str}. Camera path: {cam_text}. "
                f"Atmosphere: {light_text}. "
                f"Coherence: continuous geometric consistency, lifelike physical drag, authentic particle effects."
            )

        negatives = [
            "temporal warping",
            "flicker",
            "blurry edges",
            "distorted proportions",
            "jerky camera",
            "synthetic artifacts",
            "logo",
            "watermark",
        ]
        if scene.negative_constraints:
            negatives.extend(scene.negative_constraints)

        negative_prompt = ", ".join(negatives)

        settings = {
            "Model": "Seedance Video 1.0",
            "Aspect Ratio": scene.aspect_ratio or "16:9",
            "Duration": scene.duration or "5s",
            "Dynamics": "High Fidelity",
            "Mode": mode.value,
        }

        return prompt, negative_prompt, settings

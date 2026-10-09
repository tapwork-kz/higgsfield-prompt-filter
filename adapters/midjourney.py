"""
Midjourney v6.1 Prompt Adapter.
Tailored for Midjourney image generation with parameter flags (--ar, --v 6.1, --style raw),
clean comma-separated visual descriptors, optics, and photography styles.
"""

from typing import Tuple, Dict, Any
from adapters.base import BasePromptAdapter
from models.schemas import SceneStructure, ProcessingMode


class MidjourneyAdapter(BasePromptAdapter):
    model_name = "Midjourney"

    def adapt(
        self,
        scene: SceneStructure,
        mode: ProcessingMode = ProcessingMode.PRO,
    ) -> Tuple[str, str, Dict[str, Any]]:
        subject_str = ", ".join(scene.subject) if scene.subject else "subject"
        action_str = scene.action.primary_action or "in position"
        cam_text = self._extract_camera_string(scene)
        env_text = self._extract_environment_string(scene)
        light_text = self._extract_lighting_string(scene)

        ar = scene.aspect_ratio or "16:9"

        preservation = ""
        if scene.constraints:
            preservation = f"{', '.join(scene.constraints)}, "

        if mode == ProcessingMode.FAST:
            prompt = f"{preservation}{subject_str} {action_str}, {env_text}, {light_text}, {cam_text} --ar {ar} --v 6.1 --style raw"
        else:
            prompt = (
                f"{preservation}{subject_str} {action_str}, {env_text}, {light_text}, "
                f"{cam_text}, 35mm photograph, editorial cinematography, hyper-detailed textures, "
                f"Kodak Portra color grading --ar {ar} --v 6.1 --style raw"
            )

        negatives = [
            "illustration",
            "3d render",
            "cartoon",
            "blurry",
            "distorted faces",
            "extra fingers",
        ]
        if scene.negative_constraints:
            negatives.extend(scene.negative_constraints)

        negative_prompt = f"--no {' '.join(negatives)}"

        settings = {
            "Model": "Midjourney v6.1",
            "Aspect Ratio": ar,
            "Style": "raw",
            "Version": "6.1",
            "Mode": mode.value,
        }

        return prompt, negative_prompt, settings

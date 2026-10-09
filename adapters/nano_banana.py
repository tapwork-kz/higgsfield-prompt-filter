"""
Nano Banana Prompt Adapter.
Optimized for lightweight and ultra-fast generative models requiring dense,
concise token structures and high prompt efficiency without conversational filler.
"""

from typing import Tuple, Dict, Any
from adapters.base import BasePromptAdapter
from models.schemas import SceneStructure, ProcessingMode


class NanoBananaAdapter(BasePromptAdapter):
    model_name = "Nano Banana"

    def adapt(
        self,
        scene: SceneStructure,
        mode: ProcessingMode = ProcessingMode.PRO,
    ) -> Tuple[str, str, Dict[str, Any]]:
        subject_str = ", ".join(scene.subject) if scene.subject else "subject"
        action_str = scene.action.primary_action or "active"

        cam_parts = []
        if scene.camera.shot_type:
            cam_parts.append(scene.camera.shot_type)
        if scene.camera.lens:
            cam_parts.append(scene.camera.lens)
        if scene.camera.movement:
            cam_parts.append(scene.camera.movement)
        cam_token = ", ".join(cam_parts) or "cinematic shot"

        env_parts = []
        if scene.environment.location:
            env_parts.append(scene.environment.location)
        if scene.environment.weather:
            env_parts.append(scene.environment.weather)
        env_token = ", ".join(env_parts) or "detailed scene"

        light_token = scene.lighting.time_of_day or scene.lighting.lighting_type or "realistic lighting"

        preservation = ""
        if scene.constraints:
            preservation = f"(preserve: {', '.join(scene.constraints)}:1.3), "

        if mode == ProcessingMode.FAST:
            prompt = f"{preservation}{subject_str}, {action_str}, {cam_token}, {env_token}, {light_token}, crisp focus"
        else:
            prompt = (
                f"{preservation}{subject_str}, {action_str}, ({cam_token}:1.2), "
                f"({env_token}:1.1), {light_token}, depth of field, raw photo, realistic textures"
            )

        negatives = [
            "blurry",
            "lowres",
            "deformed",
            "bad anatomy",
            "extra limbs",
            "artifacts",
        ]
        if scene.negative_constraints:
            negatives.extend(scene.negative_constraints)

        negative_prompt = ", ".join(negatives)

        settings = {
            "Model": "Nano Banana v2",
            "Aspect Ratio": scene.aspect_ratio or "16:9",
            "Token Economy": "High",
            "Mode": mode.value,
        }

        return prompt, negative_prompt, settings

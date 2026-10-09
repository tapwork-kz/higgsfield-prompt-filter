"""
Google Veo Prompt Adapter.
Tailored for Google Veo / Veo 2 video generation model with cinematic tags,
high visual continuity, and precise director instructions.
"""

from typing import Tuple, Dict, Any
from adapters.base import BasePromptAdapter
from models.schemas import SceneStructure, ProcessingMode


class VeoAdapter(BasePromptAdapter):
    model_name = "Veo"

    def adapt(
        self,
        scene: SceneStructure,
        mode: ProcessingMode = ProcessingMode.PRO,
    ) -> Tuple[str, str, Dict[str, Any]]:
        subject_str = ", ".join(scene.subject) if scene.subject else "subject"
        action_str = scene.action.primary_action or "in fluid motion"
        cam_text = self._extract_camera_string(scene)
        env_text = self._extract_environment_string(scene)
        light_text = self._extract_lighting_string(scene)

        preservation = ""
        if scene.constraints:
            preservation = f"[MANDATORY: {', '.join(scene.constraints)}] "

        if mode == ProcessingMode.FAST:
            prompt = (
                f"{preservation}Cinematic 24fps shot of {subject_str} {action_str}. "
                f"Camera: {cam_text}. Environment: {env_text}. Lighting: {light_text}. 4K film stock, sharp focus."
            )
        else:
            prompt = (
                f"{preservation}A cinematic masterpiece sequence recorded on 35mm film stock. "
                f"[SHOT TYPE & CAMERA]: {cam_text}. "
                f"[SCENE ACTION]: {subject_str} {action_str}. "
                f"[ENVIRONMENT]: {env_text}. "
                f"[LIGHTING & ATMOSPHERE]: {light_text}. "
                f"[TEMPORAL STABILITY]: Maintain zero flicker, preserve vehicle and character identity, seamless physics and natural velocity."
            )

        negatives = [
            "temporal morphing",
            "flickering",
            "frame ghosting",
            "low bitrate artifacts",
            "unrealistic motion vector",
            "cgi plastic skin",
            "floating objects",
            "watermark",
            "subtitles",
        ]
        if scene.negative_constraints:
            negatives.extend(scene.negative_constraints)

        negative_prompt = ", ".join(negatives)

        settings = {
            "Model": "Google Veo 2",
            "Aspect Ratio": scene.aspect_ratio or "16:9",
            "Duration": scene.duration or "5s",
            "Framerate": "24fps",
            "Mode": mode.value,
        }

        return prompt, negative_prompt, settings

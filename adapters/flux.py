"""
Flux.1 Prompt Adapter (Schnell / Dev).
Follows Flux's ideal prompt architecture: highly naturalistic descriptive sentences,
exact optics, zero hollow buzzwords (avoids "photorealistic, 8k, masterpiece"),
focusing on tangible textures, lighting physics, and composition.
"""

from typing import Tuple, Dict, Any
from adapters.base import BasePromptAdapter
from models.schemas import SceneStructure, ProcessingMode


class FluxAdapter(BasePromptAdapter):
    model_name = "Flux"

    def adapt(
        self,
        scene: SceneStructure,
        mode: ProcessingMode = ProcessingMode.PRO,
    ) -> Tuple[str, str, Dict[str, Any]]:
        subject_str = ", ".join(scene.subject) if scene.subject else "subject"
        action_str = scene.action.primary_action or "positioned naturally"
        cam_text = self._extract_camera_string(scene)
        env_text = self._extract_environment_string(scene)
        light_text = self._extract_lighting_string(scene)

        preservation = ""
        if scene.constraints:
            preservation = f"Exact visual identity preserved: {', '.join(scene.constraints)}. "

        lens_spec = scene.camera.lens or "35mm prime lens at f/2.0"

        if mode == ProcessingMode.FAST:
            prompt = (
                f"{preservation}A clear photographic capture of {subject_str} {action_str}. "
                f"Shot on {lens_spec}, {cam_text}. Setting is {env_text} under {light_text}. "
                f"Fine grain, natural tactile textures."
            )
        else:
            prompt = (
                f"{preservation}A candid, authentic photograph of {subject_str} {action_str}. "
                f"Captured with {lens_spec}, utilizing {cam_text}. "
                f"The environment is {env_text}. "
                f"Illumination is characterized by {light_text}. "
                f"Tactile surface details, true-to-life color grading, subtle film grain, physically accurate specular highlights."
            )

        # Flux does not use standard negative prompt embeddings as heavily, but keeps strict exclusion list
        negatives = [
            "oversmoothed skin",
            "plastic sheen",
            "digital illustration look",
            "extra limbs",
            "airbrushed textures",
            "hallucinated geometry",
        ]
        if scene.negative_constraints:
            negatives.extend(scene.negative_constraints)

        negative_prompt = ", ".join(negatives)

        settings = {
            "Model": "Flux.1 Dev",
            "Aspect Ratio": scene.aspect_ratio or "16:9",
            "Steps": "28",
            "Guidance Scale": "3.5",
            "Mode": mode.value,
        }

        return prompt, negative_prompt, settings

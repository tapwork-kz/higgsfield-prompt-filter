"""
Kling AI Prompt Adapter.
Optimizes prompts for Kling video generation model with physical dynamics,
fluid motion, realistic camera tracking, and temporal consistency.
"""

from typing import Tuple, Dict, Any
from adapters.base import BasePromptAdapter
from models.schemas import SceneStructure, ProcessingMode, TaskType


class KlingAdapter(BasePromptAdapter):
    model_name = "Kling"

    def adapt(
        self,
        scene: SceneStructure,
        mode: ProcessingMode = ProcessingMode.PRO,
    ) -> Tuple[str, str, Dict[str, Any]]:
        subject_str = ", ".join(scene.subject) if scene.subject else "main subject"
        action_str = scene.action.primary_action or "in motion"
        
        # Build Kling specific camera & motion instructions
        cam_text = self._extract_camera_string(scene)
        env_text = self._extract_environment_string(scene)
        light_text = self._extract_lighting_string(scene)

        # Preserved identity / features
        preservation = ""
        if scene.constraints:
            preservation = f"CRITICAL CONSTRAINTS: {', '.join(scene.constraints)}. "

        if mode == ProcessingMode.FAST:
            prompt = (
                f"{preservation}{subject_str} {action_str}. {cam_text}, {env_text}, {light_text}. "
                f"Physically accurate motion, realistic reflections, 4k quality."
            )
        else:
            # Detailed PRO mode prompt with camera dynamics and physics
            parts = []
            if preservation:
                parts.append(preservation.strip())
            
            parts.append(f"SUBJECT: {subject_str}")
            if scene.appearance:
                parts.append(f"APPEARANCE: {scene.appearance}")
            
            parts.append(f"ACTION: {action_str}")
            if scene.action.dynamics:
                parts.append(f"DYNAMICS: {scene.action.dynamics}")
            
            parts.append(f"CAMERA: {cam_text}")
            parts.append(f"ENVIRONMENT: {env_text}")
            parts.append(f"LIGHTING: {light_text}")
            
            if scene.task_type == TaskType.VIDEO:
                temporal = scene.motion.temporal_consistency or "maintain consistent geometry and reflections throughout the clip"
                parts.append(f"TEMPORAL CONSISTENCY: {temporal}")
                physics = scene.motion.physics or "natural fluid dynamics and realistic inertia"
                parts.append(f"PHYSICS: {physics}")

            prompt = " | ".join(parts)

        # Negative constraints
        negatives = [
            "deformed anatomy",
            "teleporting objects",
            "glitchy motion",
            "erratic camera shake",
            "warped geometry",
            "oversaturated digital look",
            "text",
            "watermark",
            "low resolution blur",
        ]
        if scene.negative_constraints:
            negatives.extend(scene.negative_constraints)
        
        negative_prompt = ", ".join(negatives)

        settings = {
            "Model": "Kling 1.5 Pro",
            "Aspect Ratio": scene.aspect_ratio or "16:9",
            "Duration": scene.duration or "5s",
            "Motion Value": "5",
            "Mode": mode.value,
        }

        return prompt, negative_prompt, settings

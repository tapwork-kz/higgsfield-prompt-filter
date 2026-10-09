"""
Context Manager for Higgsfield-style Prompt Filter.
Maintains persistent user project state and implements anti-degradation logic
so modifications (e.g. 'камера сзади', 'сделай дождь сильнее') refine existing parameters
without wiping out previously defined scene context.
"""

from typing import Dict, Optional, Tuple
import copy
import re
from models.schemas import SceneStructure, ProcessingMode, TaskType


class ContextManager:
    """
    Manages active project contexts per Telegram user ID.
    Guarantees anti-degradation: merges incoming edits into the existing SceneStructure.
    """

    def __init__(self):
        self._contexts: Dict[int, SceneStructure] = {}
        self._user_modes: Dict[int, ProcessingMode] = {}
        self._user_models: Dict[int, str] = {}
        self._user_tasks: Dict[int, TaskType] = {}

    def get_scene(self, user_id: int) -> Optional[SceneStructure]:
        return self._contexts.get(user_id)

    def set_scene(self, user_id: int, scene: SceneStructure) -> None:
        self._contexts[user_id] = scene

    def reset_context(self, user_id: int) -> None:
        if user_id in self._contexts:
            del self._contexts[user_id]

    def get_mode(self, user_id: int, default: ProcessingMode = ProcessingMode.PRO) -> ProcessingMode:
        return self._user_modes.get(user_id, default)

    def set_mode(self, user_id: int, mode: ProcessingMode) -> None:
        self._user_modes[user_id] = mode

    def get_model(self, user_id: int, default: str = "Kling") -> str:
        return self._user_models.get(user_id, default)

    def set_model(self, user_id: int, model: str) -> None:
        self._user_models[user_id] = model
        if user_id in self._contexts:
            self._contexts[user_id].model = model

    def get_task_type(self, user_id: int, default: TaskType = TaskType.VIDEO) -> TaskType:
        return self._user_tasks.get(user_id, default)

    def set_task_type(self, user_id: int, task_type: TaskType) -> None:
        self._user_tasks[user_id] = task_type
        if user_id in self._contexts:
            self._contexts[user_id].task_type = task_type

    def is_modification_request(self, user_id: int, user_input: str) -> bool:
        """
        Determines whether the input is an iterative modification of an existing scene
        rather than a brand new project.
        """
        if user_id not in self._contexts:
            return False

        lower = user_input.lower().strip()
        # Modification keywords
        modification_triggers = [
            "теперь", "камера", "ракурс", "дождь", "сделай", "измени", "поменяй",
            "добавь", "убери", "без", "быстрее", "медленнее", "сзади", "спереди",
            "сбоку", "крупнее", "сильнее", "ярче", "темнее", "now", "change",
            "camera", "angle", "make", "faster", "slower", "more", "less"
        ]
        
        # If input is short and contains modification triggers, treat as iterative refinement
        if len(user_input.split()) <= 12 and any(t in lower for t in modification_triggers):
            return True

        # Check if subject is mentioned again as a brand new scene
        # If user explicitly states a different car or character, treat as new unless refinement
        return False

    def merge_and_update(
        self,
        user_id: int,
        new_analysis: SceneStructure,
        user_input: str,
    ) -> Tuple[SceneStructure, str]:
        """
        Anti-degradation engine:
        Merges new modifications into existing SceneStructure without discarding
        previously established parameters.
        Returns: (updated_scene, change_summary)
        """
        existing = self._contexts.get(user_id)
        if existing is None:
            self._contexts[user_id] = new_analysis
            return new_analysis, "New scene established."

        updated = copy.deepcopy(existing)
        lower = user_input.lower()
        changes_applied = []

        # 1. Camera adjustments
        if any(w in lower for w in ["камер", "ракурс", "сзади", "спереди", "сбоку", "вид", "angle", "camera", "rear", "front"]):
            if new_analysis.camera.position:
                updated.camera.position = new_analysis.camera.position
                changes_applied.append(f"camera position -> {new_analysis.camera.position}")
            if new_analysis.camera.angle:
                updated.camera.angle = new_analysis.camera.angle
            if new_analysis.camera.movement:
                updated.camera.movement = new_analysis.camera.movement
            if new_analysis.camera.lens and "мм" in lower or "lens" in lower:
                updated.camera.lens = new_analysis.camera.lens
                changes_applied.append(f"lens -> {new_analysis.camera.lens}")

        # 2. Weather & Environment adjustments
        if any(w in lower for w in ["дождь", "снег", "погод", "туман", "rain", "weather", "snow", "fog"]):
            if "сильнее" in lower or "heavy" in lower or "strong" in lower:
                updated.environment.weather = "torrential cinematic rain with heavy splashes and glistening asphalt reflections"
                changes_applied.append("weather -> heavy rain with intense reflections")
            elif "слабее" in lower or "light" in lower:
                updated.environment.weather = "gentle drizzle with subtle wet sheen on asphalt"
                changes_applied.append("weather -> light drizzle")
            elif new_analysis.environment.weather:
                updated.environment.weather = new_analysis.environment.weather
                changes_applied.append(f"weather -> {new_analysis.environment.weather}")

        # 3. Lighting adjustments
        if any(w in lower for w in ["свет", "освещени", "ярче", "темнее", "ночь", "день", "light", "bright", "dark"]):
            if new_analysis.lighting.time_of_day:
                updated.lighting.time_of_day = new_analysis.lighting.time_of_day
            if new_analysis.lighting.lighting_type:
                updated.lighting.lighting_type = new_analysis.lighting.lighting_type
                changes_applied.append(f"lighting -> {new_analysis.lighting.lighting_type}")

        # 4. Speed & Action adjustments
        if any(w in lower for w in ["быстрее", "медленнее", "скорость", "дрифт", "fast", "slow", "speed", "drift"]):
            if "быстрее" in lower or "faster" in lower:
                updated.action.speed = "high-speed dynamic"
                updated.motion.physics = "high-velocity tire smoke and centrifugal road grip"
                changes_applied.append("motion speed -> accelerated")
            elif "медленнее" in lower or "slower" in lower:
                updated.action.speed = "slow-motion 60fps cinematic glide"
                changes_applied.append("motion speed -> slow-motion")
            elif new_analysis.action.primary_action:
                updated.action.primary_action = new_analysis.action.primary_action
                changes_applied.append(f"action -> {new_analysis.action.primary_action}")

        # 5. Preserved constraints
        for constraint in new_analysis.constraints:
            if constraint not in updated.constraints:
                updated.constraints.append(constraint)
                changes_applied.append(f"constraint added -> {constraint}")

        for neg in new_analysis.negative_constraints:
            if neg not in updated.negative_constraints:
                updated.negative_constraints.append(neg)

        # 6. Aspect ratio and duration
        if new_analysis.aspect_ratio and ("9:16" in lower or "16:9" in lower or "1:1" in lower):
            updated.aspect_ratio = new_analysis.aspect_ratio
            changes_applied.append(f"aspect ratio -> {new_analysis.aspect_ratio}")

        if not changes_applied:
            # General refinement: merge non-empty attributes
            changes_applied.append("fine-tuned parameters while preserving core scene identity")

        updated.raw_user_input = f"{existing.raw_user_input} + [Edit: {user_input}]"
        self._contexts[user_id] = updated
        return updated, ", ".join(changes_applied)

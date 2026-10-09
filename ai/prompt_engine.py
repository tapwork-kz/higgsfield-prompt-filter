"""
Prompt Engine for Higgsfield-style Prompt Filter.
Main orchestration layer connecting SceneAnalyzer, ContextManager, DirectorEngine,
and Model Adapters into production-ready prompts.
"""

from typing import Optional, Dict, Any, List, Tuple
from models.schemas import (
    SceneStructure,
    ProcessingMode,
    TaskType,
    GeneratedPromptResult,
)
from ai.analyzer import SceneAnalyzer
from ai.context import ContextManager
from ai.director import DirectorEngine
from adapters import PromptAdapter


class PromptEngine:
    """
    High-level engine that processes incoming user inputs and turns them into
    clean, production-ready, copy-pasteable prompts for generative models.
    """

    def __init__(self, context_manager: Optional[ContextManager] = None):
        self.analyzer = SceneAnalyzer()
        self.context_manager = context_manager or ContextManager()
        self.director_engine = DirectorEngine()

    def process(
        self,
        user_id: int,
        user_input: str,
        mode: Optional[ProcessingMode] = None,
        model: Optional[str] = None,
        task_type: Optional[TaskType] = None,
        has_image: bool = False,
        image_metadata: Optional[Dict[str, Any]] = None,
    ) -> GeneratedPromptResult:
        # Determine user preferences from context
        active_mode = mode or self.context_manager.get_mode(user_id)
        active_model = model or self.context_manager.get_model(user_id)
        active_task = task_type or self.context_manager.get_task_type(user_id)

        # 1. Check if this is an iterative refinement of existing scene
        is_modification = self.context_manager.is_modification_request(user_id, user_input)

        # 2. Analyze user input into SceneStructure
        analyzed_scene = self.analyzer.analyze(
            text=user_input,
            task_type=active_task,
            model=active_model,
            has_image=has_image,
            image_metadata=image_metadata,
        )

        # 3. Context & Anti-degradation handling
        if is_modification:
            final_scene, change_log = self.context_manager.merge_and_update(
                user_id=user_id,
                new_analysis=analyzed_scene,
                user_input=user_input,
            )
        else:
            final_scene = analyzed_scene
            self.context_manager.set_scene(user_id, final_scene)

        # 4. Check for critical missing parameters (Max 1-2 questions only if utterly ambiguous)
        clarifications = self._check_critical_clarifications(final_scene, user_input)

        # 5. Adapt for mode & model
        if active_mode == ProcessingMode.DIRECTOR and final_scene.task_type == TaskType.VIDEO:
            director_plan = self.director_engine.generate_plan(final_scene)
            
            # Combine shots into structured multi-shot prompt
            shot_prompts = []
            for shot in director_plan.shots:
                shot_prompts.append(
                    f"SHOT {shot.shot_number} ({shot.title} - {shot.duration}):\n"
                    f"CAMERA: {shot.camera}\n"
                    f"ACTION: {shot.action}\n"
                    f"LIGHTING: {shot.lighting}\n"
                    f"PROMPT: {shot.prompt}"
                )

            full_prompt = (
                f"CONCEPT:\n{director_plan.concept}\n\n"
                f"VISUAL TONE:\n{director_plan.visual_tone}\n\n"
                + "\n\n".join(shot_prompts)
            )

            _, negative_prompt, settings = PromptAdapter(
                model=active_model,
                task=final_scene.task_type,
                scene_input=final_scene,
                mode=ProcessingMode.PRO,
            )
            settings["Mode"] = "DIRECTOR (Multi-Shot)"

            return GeneratedPromptResult(
                prompt=full_prompt,
                negative_constraints=negative_prompt,
                settings=settings,
                mode=active_mode,
                structured_scene=final_scene,
                director_plan=director_plan,
                clarification_questions=clarifications,
            )

        # FAST or PRO mode
        prompt_text, negative_text, settings_dict = PromptAdapter(
            model=active_model,
            task=final_scene.task_type,
            scene_input=final_scene,
            mode=active_mode,
        )

        return GeneratedPromptResult(
            prompt=prompt_text,
            negative_constraints=negative_text,
            settings=settings_dict,
            mode=active_mode,
            structured_scene=final_scene,
            clarification_questions=clarifications,
        )

    def _check_critical_clarifications(
        self, scene: SceneStructure, raw_text: str
    ) -> List[str]:
        questions = []
        # If the input is only 1-2 very abstract words without any subject
        if not scene.subject or (len(scene.subject) == 1 and scene.subject[0] == "subject"):
            questions.append("Какой конкретно объект или персонаж должен быть в центре кадра?")
        return questions[:2]

    @staticmethod
    def format_telegram_output(result: GeneratedPromptResult) -> str:
        """
        Formats final output strictly as specified:
        PROMPT:
        [готовый prompt]

        NEGATIVE / CONSTRAINTS:
        [ограничения]

        SETTINGS:
        Model: ...
        Aspect Ratio: ...
        Duration: ...
        """
        settings_lines = []
        for k, v in result.settings.items():
            settings_lines.append(f"{k}: {v}")
        settings_block = "\n".join(settings_lines)

        constraints_block = result.negative_constraints
        if result.structured_scene.constraints:
            preserved_str = "\n".join([f"• {c}" for c in result.structured_scene.constraints])
            constraints_block = f"PRESERVED MANDATORY RULES:\n{preserved_str}\n\nNEGATIVE EXCLUSIONS:\n{constraints_block}"

        text = (
            f"PROMPT:\n"
            f"<code>{result.prompt}</code>\n\n"
            f"NEGATIVE / CONSTRAINTS:\n"
            f"<code>{constraints_block}</code>\n\n"
            f"SETTINGS:\n"
            f"{settings_block}"
        )
        return text

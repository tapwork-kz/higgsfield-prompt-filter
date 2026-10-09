"""
Tests for Prompt Engine, Scene Decomposition, and Context Anti-Degradation.
"""

import pytest
from ai.prompt_engine import PromptEngine
from ai.context import ContextManager
from models.schemas import ProcessingMode, TaskType


def test_scene_decomposition_bmw_almaty():
    engine = PromptEngine()
    user_id = 1001
    user_input = "Сделай красивое видео BMW E39 ночью в Алматы"

    result = engine.process(
        user_id=user_id,
        user_input=user_input,
        mode=ProcessingMode.PRO,
        model="Kling",
        task_type=TaskType.VIDEO,
    )

    assert result is not None
    assert "BMW" in " ".join(result.structured_scene.subject)
    assert result.structured_scene.environment.location is not None
    assert "almaty" in result.structured_scene.environment.location.lower()
    assert result.structured_scene.lighting.time_of_day == "night"
    assert result.structured_scene.camera.lens is not None
    assert result.settings["Model"] == "Kling 1.5 Pro"
    assert result.settings["Aspect Ratio"] == "16:9"


def test_constraint_preservation():
    engine = PromptEngine()
    user_id = 1002
    user_input = "Девушка в красном платье на улице, не менять лицо человека"

    result = engine.process(
        user_id=user_id,
        user_input=user_input,
        mode=ProcessingMode.PRO,
        model="Flux",
        task_type=TaskType.IMAGE,
    )

    assert any("FACIAL FEATURES" in c or "IDENTITY" in c for c in result.structured_scene.constraints)
    assert "altered facial proportions" in result.negative_constraints.lower()


def test_image_reference_preservation():
    engine = PromptEngine()
    user_id = 1003
    user_input = "Сделай рекламный ролик с этим товаром"

    result = engine.process(
        user_id=user_id,
        user_input=user_input,
        mode=ProcessingMode.PRO,
        model="Veo",
        task_type=TaskType.VIDEO,
        has_image=True,
    )

    assert result.structured_scene.has_reference_image is True
    assert any("PRESERVE" in c for c in result.structured_scene.constraints)


def test_context_continuity_and_anti_degradation():
    context_mgr = ContextManager()
    engine = PromptEngine(context_manager=context_mgr)
    user_id = 1004

    # Step 1: Initial query
    res1 = engine.process(
        user_id=user_id,
        user_input="Сделай BMW E39 ночью в Алматы",
        mode=ProcessingMode.PRO,
        model="Kling",
    )
    assert "BMW" in " ".join(res1.structured_scene.subject)
    assert "almaty" in res1.structured_scene.environment.location.lower()

    # Step 2: Refine camera position
    res2 = engine.process(
        user_id=user_id,
        user_input="Теперь камера должна быть сзади",
    )
    # Ensure car and location were not wiped out
    assert "BMW" in " ".join(res2.structured_scene.subject)
    assert "almaty" in res2.structured_scene.environment.location.lower()
    assert "rear" in res2.structured_scene.camera.position.lower()

    # Step 3: Refine rain/weather
    res3 = engine.process(
        user_id=user_id,
        user_input="Сделай дождь сильнее",
    )
    # Ensure car, rear camera, and location are STILL preserved
    assert "BMW" in " ".join(res3.structured_scene.subject)
    assert "rear" in res3.structured_scene.camera.position.lower()
    assert "rain" in res3.structured_scene.environment.weather.lower()


def test_director_mode_multi_shot():
    engine = PromptEngine()
    user_id = 1005
    user_input = "Сделай кинематографичный ролик Porsche 911 на горном серпантине"

    result = engine.process(
        user_id=user_id,
        user_input=user_input,
        mode=ProcessingMode.DIRECTOR,
        model="Runway",
        task_type=TaskType.VIDEO,
    )

    assert result.director_plan is not None
    assert len(result.director_plan.shots) == 3
    assert "SHOT 1" in result.prompt
    assert "SHOT 2" in result.prompt
    assert "SHOT 3" in result.prompt
    assert result.settings["Mode"] == "DIRECTOR (Multi-Shot)"

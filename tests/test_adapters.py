"""
Tests for Model Adapters (PromptAdapter).
Verifies adaptation for Kling, Veo, Runway, Seedance, Flux, Nano Banana, Sora, Hailuo, Midjourney.
"""

import pytest
from adapters import PromptAdapter, get_adapter, ADAPTER_REGISTRY
from models.schemas import SceneStructure, ProcessingMode, TaskType


@pytest.fixture
def sample_scene():
    scene = SceneStructure(
        task_type=TaskType.VIDEO,
        subject=["BMW M5 E39"],
        raw_user_input="BMW M5 E39 ночью в Алматы",
    )
    scene.environment.location = "Almaty city street"
    scene.lighting.time_of_day = "night"
    scene.camera.lens = "35mm anamorphic lens"
    scene.camera.shot_type = "low-angle medium tracking shot"
    scene.action.primary_action = "accelerating smoothly over wet asphalt"
    return scene


def test_all_models_registered():
    expected_models = [
        "kling", "veo", "runway", "seedance", "flux",
        "nano_banana", "sora", "hailuo", "midjourney"
    ]
    for model in expected_models:
        assert model in ADAPTER_REGISTRY


def test_kling_adapter(sample_scene):
    prompt, neg, settings = PromptAdapter("Kling", "video", sample_scene, ProcessingMode.PRO)
    assert "BMW M5 E39" in prompt
    assert "SUBJECT:" in prompt
    assert "CAMERA:" in prompt
    assert "TEMPORAL CONSISTENCY:" in prompt
    assert "Kling" in settings["Model"]


def test_veo_adapter(sample_scene):
    prompt, neg, settings = PromptAdapter("Veo", "video", sample_scene, ProcessingMode.PRO)
    assert "[SHOT TYPE & CAMERA]:" in prompt
    assert "Google Veo 2" in settings["Model"]
    assert "flickering" in neg


def test_runway_adapter(sample_scene):
    prompt, neg, settings = PromptAdapter("Runway", "video", sample_scene, ProcessingMode.PRO)
    assert "[Camera Movement]:" in prompt
    assert "[Subject Action]:" in prompt
    assert "Runway Gen-3 Alpha" in settings["Model"]


def test_flux_adapter(sample_scene):
    sample_scene.task_type = TaskType.IMAGE
    prompt, neg, settings = PromptAdapter("Flux", "image", sample_scene, ProcessingMode.PRO)
    assert "BMW M5 E39" in prompt
    assert "Flux.1 Dev" in settings["Model"]


def test_nano_banana_adapter(sample_scene):
    prompt, neg, settings = PromptAdapter("Nano Banana", "video", sample_scene, ProcessingMode.FAST)
    assert "BMW M5 E39" in prompt
    assert "Nano Banana" in settings["Model"]


def test_sora_adapter(sample_scene):
    prompt, neg, settings = PromptAdapter("Sora", "video", sample_scene, ProcessingMode.PRO)
    assert "OpenAI Sora" in settings["Model"]
    assert "Continuous tracking shot" in prompt


def test_midjourney_adapter(sample_scene):
    prompt, neg, settings = PromptAdapter("Midjourney", "image", sample_scene, ProcessingMode.PRO)
    assert "--ar 16:9" in prompt
    assert "--v 6.1" in prompt
    assert "--no" in neg

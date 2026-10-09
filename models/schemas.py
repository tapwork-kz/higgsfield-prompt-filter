"""
Data models and schemas for Higgsfield-style Prompt Filter.
Defines intermediate representations, scene structures, and configuration types.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    EDIT = "edit"


class ProcessingMode(str, Enum):
    FAST = "FAST"
    PRO = "PRO"
    DIRECTOR = "DIRECTOR"


class SupportedModel(str, Enum):
    KLING = "Kling"
    VEO = "Veo"
    RUNWAY = "Runway"
    SEEDANCE = "Seedance"
    FLUX = "Flux"
    NANO_BANANA = "Nano Banana"
    SORA = "Sora"
    HAILUO = "Hailuo"
    MIDJOURNEY = "Midjourney"


class CameraSpec(BaseModel):
    position: Optional[str] = None
    movement: Optional[str] = None
    angle: Optional[str] = None
    lens: Optional[str] = None
    shot_type: Optional[str] = None
    speed: Optional[str] = None
    depth_of_field: Optional[str] = None
    focus: Optional[str] = None


class LightingSpec(BaseModel):
    lighting_type: Optional[str] = None
    source: Optional[str] = None
    time_of_day: Optional[str] = None
    mood: Optional[str] = None
    contrast: Optional[str] = None
    color_temperature: Optional[str] = None


class EnvironmentSpec(BaseModel):
    location: Optional[str] = None
    weather: Optional[str] = None
    atmosphere: Optional[str] = None
    background: Optional[str] = None
    foreground: Optional[str] = None
    details: List[str] = Field(default_factory=list)


class ActionSpec(BaseModel):
    primary_action: Optional[str] = None
    subject_movement: Optional[str] = None
    interaction: Optional[str] = None
    speed: Optional[str] = None
    dynamics: Optional[str] = None


class CompositionSpec(BaseModel):
    framing: Optional[str] = None
    perspective: Optional[str] = None
    depth: Optional[str] = None
    focal_point: Optional[str] = None


class StyleSpec(BaseModel):
    visual_style: Optional[str] = None
    realism_level: Optional[str] = "photorealistic"
    color_palette: Optional[str] = None
    textures_materials: List[str] = Field(default_factory=list)
    cinematic_characteristics: List[str] = Field(default_factory=list)


class MotionSpec(BaseModel):
    physics: Optional[str] = None
    motion_blur: Optional[str] = None
    temporal_consistency: Optional[str] = None
    background_consistency: Optional[str] = None
    transitions: Optional[str] = None


class SceneStructure(BaseModel):
    """
    Intermediate JSON specification representing the analyzed and engineered scene.
    Preserves all physical, cinematic, and compositional parameters.
    """
    task_type: TaskType = TaskType.VIDEO
    subject: List[str] = Field(default_factory=list)
    characters: List[str] = Field(default_factory=list)
    appearance: Optional[str] = None
    environment: EnvironmentSpec = Field(default_factory=EnvironmentSpec)
    action: ActionSpec = Field(default_factory=ActionSpec)
    composition: CompositionSpec = Field(default_factory=CompositionSpec)
    camera: CameraSpec = Field(default_factory=CameraSpec)
    lighting: LightingSpec = Field(default_factory=LightingSpec)
    style: StyleSpec = Field(default_factory=StyleSpec)
    motion: MotionSpec = Field(default_factory=MotionSpec)
    constraints: List[str] = Field(default_factory=list)
    negative_constraints: List[str] = Field(default_factory=list)
    model: str = "Kling"
    duration: Optional[str] = "5s"
    aspect_ratio: Optional[str] = "16:9"
    has_reference_image: bool = False
    reference_features_to_preserve: List[str] = Field(default_factory=list)
    raw_user_input: str = ""


class DirectorShot(BaseModel):
    shot_number: int
    title: str
    duration: str = "3s"
    camera: str
    action: str
    lighting: str
    visual_continuity: str
    prompt: str


class DirectorPlan(BaseModel):
    concept: str
    storyline: str
    visual_tone: str
    shots: List[DirectorShot]
    global_constraints: List[str] = Field(default_factory=list)


class GeneratedPromptResult(BaseModel):
    prompt: str
    negative_constraints: str
    settings: Dict[str, Any]
    mode: ProcessingMode
    structured_scene: SceneStructure
    director_plan: Optional[DirectorPlan] = None
    clarification_questions: List[str] = Field(default_factory=list)

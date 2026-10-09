"""
Director Mode Engine for Higgsfield-style Prompt Filter.
Generates comprehensive multi-shot cinematic concepts:
- Concept & Storyline
- Visual Tone & Lighting continuity
- Multi-shot sequence breakdown (establishing, medium action, close-up hero)
- Camera paths and optical specs for each shot
- Model-adapted prompts for each shot.
"""

from typing import List
from models.schemas import SceneStructure, DirectorPlan, DirectorShot, ProcessingMode
from adapters import PromptAdapter


class DirectorEngine:
    """
    Transforms a single scene intention into a multi-shot cinematic production plan.
    """

    def generate_plan(self, scene: SceneStructure) -> DirectorPlan:
        subject = ", ".join(scene.subject) if scene.subject else "Hero Subject"
        location = scene.environment.location or "urban atmosphere"
        lighting = scene.lighting.lighting_type or "moody cinematic illumination"

        concept = f"Cinematic showcase featuring {subject} navigating through {location} under {lighting}."
        storyline = (
            f"An atmospheric sequence beginning with an expansive establishing view of {subject}, "
            f"progressing into a high-octane dynamic motion tracking shot, and culminating in an intimate hero close-up."
        )
        visual_tone = (
            "35mm anamorphic aesthetic, controlled specular reflections on wet surfaces, "
            "deep optical blacks, authentic motion blur, and seamless temporal continuity across cuts."
        )

        shots: List[DirectorShot] = []

        # Shot 1: Establishing Shot
        shot1_scene = scene.model_copy(deep=True)
        shot1_scene.camera.shot_type = "wide establishing shot"
        shot1_scene.camera.lens = "24mm anamorphic lens"
        shot1_scene.camera.movement = "slow cinematic low-altitude forward dolly"
        shot1_scene.action.primary_action = f"emerges into frame within {location}"
        prompt1, _, _ = PromptAdapter(shot1_scene.model, shot1_scene.task_type, shot1_scene, mode=ProcessingMode.PRO)

        shots.append(
            DirectorShot(
                shot_number=1,
                title="Establishing Entrance",
                duration="3s",
                camera="24mm anamorphic lens, low-altitude dolly forward",
                action=f"{subject} establishes presence in {location}",
                lighting=lighting,
                visual_continuity="Establish environmental spatial geometry and atmospheric haze",
                prompt=prompt1,
            )
        )

        # Shot 2: Dynamic Action Tracking
        shot2_scene = scene.model_copy(deep=True)
        shot2_scene.camera.shot_type = "low-angle medium tracking shot"
        shot2_scene.camera.lens = "35mm prime lens"
        shot2_scene.camera.movement = "high-speed stabilized gimbal tracking following vehicle curvature"
        shot2_scene.action.primary_action = scene.action.primary_action or "accelerates dynamically with road traction"
        prompt2, _, _ = PromptAdapter(shot2_scene.model, shot2_scene.task_type, shot2_scene, mode=ProcessingMode.PRO)

        shots.append(
            DirectorShot(
                shot_number=2,
                title="Dynamic Kinetic Pursuit",
                duration="4s",
                camera="35mm prime, parallel tracking shot with realistic vibration compensation",
                action=f"{subject} in full kinetic momentum, water or particle displacement",
                lighting="Dynamic reflections sweeping across body surfaces",
                visual_continuity="Match vehicle velocity, color palette, and environmental wetness from Shot 1",
                prompt=prompt2,
            )
        )

        # Shot 3: Hero Close-Up & Climax
        shot3_scene = scene.model_copy(deep=True)
        shot3_scene.camera.shot_type = "dramatic low-angle hero close-up"
        shot3_scene.camera.lens = "50mm f/1.8 cinema lens"
        shot3_scene.camera.movement = "subtle slow push-in focusing on iconic contours"
        shot3_scene.action.primary_action = "glides past lens as taillight trails and reflections shimmer"
        prompt3, _, _ = PromptAdapter(shot3_scene.model, shot3_scene.task_type, shot3_scene, mode=ProcessingMode.PRO)

        shots.append(
            DirectorShot(
                shot_number=3,
                title="Hero Detail & Climax",
                duration="3s",
                camera="50mm f/1.8, slow creeping push-in with shallow depth of field",
                action=f"Dramatic focal emphasis on {subject} design contours",
                lighting="High contrast rim lighting with anamorphic bokeh orbs",
                visual_continuity="Maintain identical color grading, road moisture, and lighting temperature",
                prompt=prompt3,
            )
        )

        global_constraints = list(scene.constraints) + [
            "Maintain strict color temperature and exposure grading across all 3 shots",
            "Zero geometry alteration or badge mismatch between shots",
        ]

        return DirectorPlan(
            concept=concept,
            storyline=storyline,
            visual_tone=visual_tone,
            shots=shots,
            global_constraints=global_constraints,
        )

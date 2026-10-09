"""
Scene Analyzer for Higgsfield-style Prompt Filter.
Deconstructs raw user requests into rich, structured cinematic components.
Identifies subject, characters, environment, camera, lighting, physics, and preservation constraints.
"""

import re
from typing import Optional, List, Dict, Any
from models.schemas import (
    SceneStructure,
    CameraSpec,
    LightingSpec,
    EnvironmentSpec,
    ActionSpec,
    CompositionSpec,
    StyleSpec,
    MotionSpec,
    TaskType,
)


class SceneAnalyzer:
    """
    Decomposes human requests into technical cinematic parameters.
    Ensures user constraints are strictly preserved and non-critical
    technical cinematography parameters are professionally inferred.
    """

    def analyze(
        self,
        text: str,
        task_type: TaskType = TaskType.VIDEO,
        model: str = "Kling",
        has_image: bool = False,
        image_metadata: Optional[Dict[str, Any]] = None,
    ) -> SceneStructure:
        text_lower = text.lower()
        scene = SceneStructure(
            task_type=task_type,
            model=model,
            raw_user_input=text,
            has_reference_image=has_image,
        )

        # 1. Negative & Preservation Constraints
        self._extract_constraints(text, text_lower, scene, has_image)

        # 2. Subject & Characters
        self._extract_subject_and_characters(text, text_lower, scene)

        # 3. Environment & Location
        self._extract_environment(text, text_lower, scene)

        # 4. Camera & Lens Specifications
        self._extract_camera(text, text_lower, scene)

        # 5. Lighting & Time of Day
        self._extract_lighting(text, text_lower, scene)

        # 6. Action & Movement
        self._extract_action(text, text_lower, scene)

        # 7. Style & Aesthetics
        self._extract_style(text, text_lower, scene)

        # 8. Motion & Physics (for video)
        self._extract_motion(text, text_lower, scene)

        # 9. Format specs (aspect ratio & duration)
        self._extract_format_specs(text, text_lower, scene)

        return scene

    def _extract_constraints(
        self, raw: str, lower: str, scene: SceneStructure, has_image: bool
    ):
        # Explicit preservation instructions
        if "не менять лицо" in lower or "сохранить лицо" in lower or "keep face" in lower:
            scene.constraints.append("PRESERVE IDENTITY / DO NOT ALTER FACIAL FEATURES")
            scene.negative_constraints.append("altered facial proportions, deformed face, changed facial identity")

        if "не менять одежду" in lower or "keep clothes" in lower:
            scene.constraints.append("PRESERVE EXACT CLOTHING AND FABRIC TEXTURE")

        if "не менять цвет" in lower:
            scene.constraints.append("PRESERVE ORIGINAL COLOR PALETTE")

        # Image reference preservation rules
        if has_image:
            preservation_rule = (
                "PRESERVE THE SUBJECT’S IDENTITY, FACIAL STRUCTURE, HAIRSTYLE, "
                "CLOTHING, BODY PROPORTIONS AND KEY VISUAL FEATURES"
            )
            if preservation_rule not in scene.constraints:
                scene.constraints.append(preservation_rule)
            scene.reference_features_to_preserve.extend([
                "facial geometry",
                "wardrobe textures",
                "object contours",
                "color fidelity",
            ])

        # Negative instructions in user prompt
        # e.g., "без людей", "без дождя", "no text", "no blur"
        negative_matches = re.findall(
            r"(?:без|no|without|исключи)\s+([а-яa-z0-9\s]+?)(?:,|\.|$)", lower
        )
        for neg in negative_matches:
            cleaned = neg.strip()
            if cleaned and len(cleaned) < 30:
                scene.negative_constraints.append(f"no {cleaned}")

    def _extract_subject_and_characters(self, raw: str, lower: str, scene: SceneStructure):
        # Car / Vehicles
        car_patterns = [
            (r"\bbmw\s*(?:e\d+|m\d+|\w+)?", "BMW"),
            (r"\bmercedes(?:\s*benz|\s*amg|\s*\w+)?", "Mercedes-Benz"),
            (r"\bporsche(?:\s*911|\s*gt\d+|\s*\w+)?", "Porsche"),
            (r"\baudi(?:\s*rs\d+|\s*\w+)?", "Audi"),
            (r"\bавтомобиль|\bмашин[аыуе]|\bcar\b|\bvehicle\b", "car"),
            (r"\bмотоцикл|\bmotorcycle|\bbike\b", "motorcycle"),
        ]
        detected_subjects = []
        for pat, label in car_patterns:
            m = re.search(pat, lower)
            if m:
                # Grab actual matched text from raw for casing
                start, end = m.span()
                matched_val = raw[start:end].strip()
                detected_subjects.append(matched_val)
                scene.constraints.append(f"PRESERVE VEHICLE MODEL AND BODY DESIGN ({matched_val.upper()})")
                break

        # People / Characters
        char_patterns = [
            (r"\bдевушк[аиеу]|\bженщин[аыеу]|\bwoman\b|\bgirl\b", "young woman"),
            (r"\bпарен[ья]|\bмужчин[аыеу]|\bman\b|\bguy\b", "man"),
            (r"\bмодель\b|\bmodel\b", "fashion model"),
            (r"\bкиберпанк персонаж|\bcyberpunk character", "cyberpunk character"),
            (r"\bробот|\brobot|\bandroid", "futuristic android"),
        ]
        for pat, label in char_patterns:
            if re.search(pat, lower):
                scene.characters.append(label)

        # Products
        if "товар" in lower or "продукт" in lower or "реклама" in lower or "product" in lower:
            if not detected_subjects and not scene.characters:
                detected_subjects.append("commercial product package")
                scene.constraints.append("PRESERVE EXACT PRODUCT BRANDING AND PACKAGING")

        if not detected_subjects and not scene.characters:
            # Fallback to general nouns or first significant phrase
            cleaned = re.sub(r"(сделай|создай|красивое|видео|фото|видеоролик|please|make|generate)", "", lower).strip()
            detected_subjects.append(cleaned if cleaned else "subject")

        scene.subject = detected_subjects

    def _extract_environment(self, raw: str, lower: str, scene: SceneStructure):
        env = scene.environment

        # Locations
        city_matches = [
            ("алматы|almaty", "Almaty city street with modern urban architecture and backdrop silhouettes"),
            ("москва|moscow", "Moscow metropolitan avenue with illuminated high-rises"),
            ("токио|tokyo", "Tokyo neon-lit night avenue with glowing signs"),
            ("нью-йорк|new york", "New York City urban streetscape"),
            ("дубай|dubai", "Dubai modern skyline and illuminated highway"),
            ("горы|mountains", "scenic winding mountain pass with rugged peaks"),
            ("пустыня|desert", "open desert highway with sandy expanse"),
            ("лес|forest", "dense atmospheric forest road with mist"),
            ("студи[яи]|studio", "minimalist professional production studio with seamless cyclorama"),
        ]
        for pat, loc_desc in city_matches:
            if re.search(pat, lower):
                env.location = loc_desc
                break

        if not env.location:
            if "улиц" in lower or "street" in lower:
                env.location = "urban city street"
            elif "шоссе" in lower or "highway" in lower:
                env.location = "open asphalt highway"
            else:
                env.location = "metropolitan urban environment"

        # Weather & Atmosphere
        if re.search(r"дожд|rain|wet", lower):
            env.weather = "rainy night with glistening wet asphalt reflections and water droplets"
            env.details.append("wet asphalt reflections")
            env.details.append("subtle mist and atmospheric precipitation")
        elif re.search(r"снег|snow", lower):
            env.weather = "gentle snowfall with crisp cold atmosphere"
            env.details.append("soft falling snowflakes")
        elif re.search(r"туман|fog|mist", lower):
            env.weather = "dense cinematic fog with volumetric light beams"
        else:
            env.weather = "clear atmosphere with crisp environmental clarity"

        # Background & details
        if re.search(r"ноч|night", lower):
            env.atmosphere = "noir night ambiance with warm urban streetlamp spill"
            env.background = "softly blurred urban cityscape with bokeh light sources"
        elif re.search(r"закат|sunset|golden\s*hour", lower):
            env.atmosphere = "warm golden hour ambiance with long cinematic shadows"
            env.background = "horizon backlit by sunset gradient"
        else:
            env.atmosphere = "cinematic atmospheric depth"

    def _extract_camera(self, raw: str, lower: str, scene: SceneStructure):
        cam = scene.camera

        # Angle & Position
        if re.search(r"сзади|rear|back", lower):
            cam.position = "low rear three-quarter angle"
            cam.angle = "low-angle"
        elif re.search(r"спереди|front", lower):
            cam.position = "low front three-quarter angle"
            cam.angle = "low-angle"
        elif re.search(r"сбоку|side|profile", lower):
            cam.position = "lateral side profile tracking"
            cam.angle = "eye-level"
        elif re.search(r"сверху|top|drone|aerial", lower):
            cam.position = "aerial bird-eye view"
            cam.angle = "high-angle"
        else:
            cam.position = "low-angle tracking position"
            cam.angle = "low-angle"

        # Movement
        if re.search(r"динамичн|fast|быстр", lower):
            cam.movement = "high-speed smooth dolly tracking"
            cam.speed = "fast dynamic"
        elif re.search(r"медленн|slow", lower):
            cam.movement = "slow cinematic tracking shot"
            cam.speed = "slow elegant"
        else:
            cam.movement = "smooth stabilized gimbal tracking shot following the subject"
            cam.speed = "smooth medium"

        # Optics & Lens
        if re.search(r"портрет|portrait|85mm", lower):
            cam.lens = "85mm prime lens at f/1.8"
            cam.shot_type = "medium close-up"
            cam.depth_of_field = "shallow depth of field with creamy circular bokeh"
        elif re.search(r"общий\s*план|wide|24mm", lower):
            cam.lens = "24mm wide-angle cinema lens"
            cam.shot_type = "wide establishing shot"
            cam.depth_of_field = "deep depth of field capturing broad scenery"
        else:
            # Professional standard for automotive / cinematic
            cam.lens = "35mm anamorphic cinema lens at f/2.4"
            cam.shot_type = "low-angle medium tracking shot"
            cam.depth_of_field = "shallow depth of field with organic optical falloff"

        cam.focus = "pin-sharp focal tracking locked strictly onto the subject"

    def _extract_lighting(self, raw: str, lower: str, scene: SceneStructure):
        light = scene.lighting

        if re.search(r"ноч|night", lower):
            light.time_of_day = "night"
            light.lighting_type = "atmospheric street lighting, neon ambient glow, and sharp vehicular headlamps"
            light.contrast = "high dynamic contrast with rich deep blacks and controlled specular highlights"
            light.mood = "cinematic, moody, and sophisticated"
            light.color_temperature = "cool ambient tones contrasted with warm sodium streetlamps"
        elif re.search(r"закат|sunset|golden\s*hour", lower):
            light.time_of_day = "golden hour"
            light.lighting_type = "warm directional sunlight with golden rim lighting"
            light.contrast = "moderate contrast with soft shadow transitions"
            light.mood = "warm, nostalgic, and majestic"
        elif re.search(r"день|днем|днём|day|daylight", lower):
            light.time_of_day = "daylight"
            light.lighting_type = "natural daylight with soft diffused fill"
            light.contrast = "balanced cinematic natural contrast"
            light.mood = "clear, crisp, and vibrant"
        elif re.search(r"неон|cyberpunk|neon", lower):
            light.lighting_type = "vibrant neon rim lighting with cyan and magenta accents"
            light.contrast = "high contrast with vibrant specular reflections"
            light.mood = "futuristic cyberpunk mood"
        else:
            # Default realistic lighting
            light.lighting_type = "physically accurate studio-grade natural lighting"
            light.contrast = "cinematic natural contrast"
            light.mood = "premium editorial"

    def _extract_action(self, raw: str, lower: str, scene: SceneStructure):
        act = scene.action

        if re.search(r"дрифт|drift", lower):
            act.primary_action = "drifting smoothly through an asphalt curve"
            act.dynamics = "controlled counter-steering, gentle tire smoke, and subtle vehicle body roll"
        elif re.search(r"едет|движ|drive|cruis|ride", lower) or any(s in " ".join(scene.subject).lower() for s in ["bmw", "car", "mercedes"]):
            act.primary_action = "cruising smoothly along the illuminated asphalt"
            act.dynamics = "natural suspension movement, spinning alloy wheels, and light road spray"
        elif re.search(r"бежит|бег|run", lower):
            act.primary_action = "running with purposeful dynamic momentum"
            act.dynamics = "natural physical exertion, realistic clothing movement"
        elif re.search(r"реклама|commercial|товар", lower):
            act.primary_action = "hero product showcase with elegant subtle rotation"
            act.dynamics = "smooth 360 showcase with light sweeping across premium surfaces"
        else:
            act.primary_action = "fluid organic movement maintaining natural posture"
            act.dynamics = "realistic physical weight and inertia"

    def _extract_style(self, raw: str, lower: str, scene: SceneStructure):
        style = scene.style
        style.realism_level = "photorealistic live-action cinema"
        style.visual_style = "35mm motion picture film stock"
        style.textures_materials = [
            "realistic metallic car paint clear-coat reflections",
            "micro-textures on asphalt and surrounding surfaces",
            "physically accurate glass refraction",
        ]
        style.cinematic_characteristics = [
            "natural optical motion blur",
            "anamorphic subtle horizontal streak highlights",
            "true color grading without artificial oversaturation",
        ]

    def _extract_motion(self, raw: str, lower: str, scene: SceneStructure):
        motion = scene.motion
        motion.physics = "authentic physical inertia, weight distribution, and road traction"
        motion.motion_blur = "shutter angle 180-degree natural cinematic motion blur"
        motion.temporal_consistency = (
            "strict temporal consistency across all frames; preserve vehicle geometry, "
            "wheel rotation speed, reflections, and surrounding environment without warping"
        )
        motion.background_consistency = "seamless parallax background scrolling without artifacts"

    def _extract_format_specs(self, raw: str, lower: str, scene: SceneStructure):
        # Aspect Ratio
        if "9:16" in lower or "вертикальн" in lower or "story" in lower or "reels" in lower:
            scene.aspect_ratio = "9:16"
        elif "1:1" in lower or "квадрат" in lower:
            scene.aspect_ratio = "1:1"
        elif "4:5" in lower:
            scene.aspect_ratio = "4:5"
        elif "2.39:1" in lower or "anamorphic" in lower or "кино" in lower:
            scene.aspect_ratio = "16:9"
        else:
            scene.aspect_ratio = "16:9"

        # Duration
        dur_match = re.search(r"(\d+)\s*(?:сек|sec|s\b)", lower)
        if dur_match:
            scene.duration = f"{dur_match.group(1)}s"
        else:
            scene.duration = "5s"

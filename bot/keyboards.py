"""
Telegram Keyboards and UI Components for Higgsfield Prompt Filter.
Provides main quick-action buttons and inline settings selectors.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from models.schemas import SupportedModel, ProcessingMode, TaskType


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Standard reply keyboard matching requirements:
    [IMAGE], [VIDEO], [EDIT IMAGE], [ENHANCE PROMPT], [CHANGE MODEL], [GENERATE]
    """
    keyboard = [
        [KeyboardButton("🎬 [VIDEO]"), KeyboardButton("🖼️ [IMAGE]")],
        [KeyboardButton("🎨 [EDIT IMAGE]"), KeyboardButton("⚡ [ENHANCE PROMPT]")],
        [KeyboardButton("🤖 [CHANGE MODEL]"), KeyboardButton("🚀 [GENERATE]")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_models_inline_keyboard(current_model: str = "Kling") -> InlineKeyboardMarkup:
    """Inline keyboard for switching active generative model."""
    models = [
        ("Kling 1.5", "Kling"),
        ("Google Veo 2", "Veo"),
        ("Runway Gen-3", "Runway"),
        ("Seedance", "Seedance"),
        ("Flux.1", "Flux"),
        ("Nano Banana", "Nano Banana"),
        ("OpenAI Sora", "Sora"),
        ("MiniMax Hailuo", "Hailuo"),
        ("Midjourney v6.1", "Midjourney"),
    ]
    buttons = []
    row = []
    for label, val in models:
        prefix = "✅ " if val.lower() == current_model.lower() else ""
        row.append(InlineKeyboardButton(f"{prefix}{label}", callback_data=f"set_model:{val}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(buttons)


def get_modes_inline_keyboard(current_mode: str = "PRO") -> InlineKeyboardMarkup:
    """Inline keyboard for switching analysis mode."""
    modes = [
        ("⚡ FAST (Quick)", "FAST"),
        ("🎯 PRO (Deep Scene)", "PRO"),
        ("🎬 DIRECTOR (Multi-Shot)", "DIRECTOR"),
    ]
    buttons = []
    for label, val in modes:
        prefix = "✅ " if val == current_mode else ""
        buttons.append([InlineKeyboardButton(f"{prefix}{label}", callback_data=f"set_mode:{val}")])
    return InlineKeyboardMarkup(buttons)


def get_prompt_actions_keyboard(has_director: bool = False) -> InlineKeyboardMarkup:
    """Quick actions attached under each generated prompt."""
    buttons = [
        [
            InlineKeyboardButton("⚡ FAST Mode", callback_data="regen:FAST"),
            InlineKeyboardButton("🎯 PRO Mode", callback_data="regen:PRO"),
            InlineKeyboardButton("🎬 DIRECTOR", callback_data="regen:DIRECTOR"),
        ],
        [
            InlineKeyboardButton("🔄 Change Model", callback_data="open_models"),
            InlineKeyboardButton("🗑️ New Scene (/new)", callback_data="action_new"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)

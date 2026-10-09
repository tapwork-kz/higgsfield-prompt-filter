"""
Telegram Command and Message Handlers for Higgsfield Prompt Filter.
Integrates user interactions, context retention, and prompt generation.
"""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ai.prompt_engine import PromptEngine
from ai.context import ContextManager
from models.schemas import ProcessingMode, TaskType
from bot.keyboards import (
    get_main_reply_keyboard,
    get_models_inline_keyboard,
    get_modes_inline_keyboard,
    get_prompt_actions_keyboard,
)

# Shared singleton instances for runtime
context_manager = ContextManager()
prompt_engine = PromptEngine(context_manager=context_manager)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /start command."""
    user = update.effective_user
    greeting = (
        f"👋 Привет, {user.first_name or 'пользователь'}!\n\n"
        "Я — <b>Higgsfield AI Prompt Filter</b>.\n\n"
        "Я не просто улучшаю текст, а работаю как профессиональный режиссёр и оператор:\n"
        "• Анализирую глубину сцены, оптику, движение камеры, свет и физику\n"
        "• Сохраняю важные ограничения (лицо, объект, пропорции)\n"
        "• Адаптирую финальный prompt под выбранную модель (Kling, Veo, Runway, Flux, Sora, Midjourney и др.)\n\n"
        "<b>Команды:</b>\n"
        "/new — Начать новую сцену с чистого листа\n"
        "/video — Переключить задачу на генерацию видео\n"
        "/image — Переключить задачу на генерацию фото\n"
        "/edit — Режим редактирования референса\n"
        "/models — Выбрать целевую нейросеть\n"
        "/settings — Настройки режима (FAST / PRO / DIRECTOR)\n\n"
        "Просто напиши, что ты хочешь создать, например:\n"
        "<i>«Сделай красивое видео BMW E39 ночью в Алматы»</i>"
    )
    await update.message.reply_text(
        greeting,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_reply_keyboard(),
    )


async def new_scene_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /new command to reset scene context."""
    user_id = update.effective_user.id
    context_manager.reset_context(user_id)
    await update.message.reply_text(
        "✨ <b>Контекст проекта сброшен!</b>\nОтправьте новый запрос или изображение.",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_reply_keyboard(),
    )


async def video_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets active task to VIDEO."""
    user_id = update.effective_user.id
    context_manager.set_task_type(user_id, TaskType.VIDEO)
    await update.message.reply_text(
        "🎬 Режим установлен: <b>Генерация видео</b>. Напишите ваш запрос.",
        parse_mode=ParseMode.HTML,
    )


async def image_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets active task to IMAGE."""
    user_id = update.effective_user.id
    context_manager.set_task_type(user_id, TaskType.IMAGE)
    await update.message.reply_text(
        "🖼️ Режим установлен: <b>Генерация изображений</b>. Напишите ваш запрос.",
        parse_mode=ParseMode.HTML,
    )


async def edit_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets active task to EDIT."""
    user_id = update.effective_user.id
    context_manager.set_task_type(user_id, TaskType.EDIT)
    await update.message.reply_text(
        "🎨 Режим установлен: <b>Редактирование изображения</b>.\nПрикрепите изображение и опишите, что нужно изменить.",
        parse_mode=ParseMode.HTML,
    )


async def models_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /models command."""
    user_id = update.effective_user.id
    current_model = context_manager.get_model(user_id)
    await update.message.reply_text(
        f"🤖 Выберите целевую генеративную модель (текущая: <b>{current_model}</b>):",
        parse_mode=ParseMode.HTML,
        reply_markup=get_models_inline_keyboard(current_model),
    )


async def settings_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /settings command."""
    user_id = update.effective_user.id
    current_mode = context_manager.get_mode(user_id)
    current_model = context_manager.get_model(user_id)
    current_task = context_manager.get_task_type(user_id)

    info = (
        f"⚙️ <b>Текущие настройки:</b>\n"
        f"• Модель: <b>{current_model}</b>\n"
        f"• Режим анализа: <b>{current_mode.value}</b>\n"
        f"• Задача: <b>{current_task.value}</b>\n\n"
        "Выберите режим работы Prompt Filter:"
    )
    await update.message.reply_text(
        info,
        parse_mode=ParseMode.HTML,
        reply_markup=get_modes_inline_keyboard(current_mode.value),
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes incoming text messages and main menu keyboard clicks."""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user_id = update.effective_user.id

    # Handle menu buttons
    if "🎬 [VIDEO]" in text:
        await video_command_handler(update, context)
        return
    elif "🖼️ [IMAGE]" in text:
        await image_command_handler(update, context)
        return
    elif "🎨 [EDIT IMAGE]" in text:
        await edit_command_handler(update, context)
        return
    elif "🤖 [CHANGE MODEL]" in text:
        await models_command_handler(update, context)
        return
    elif "⚡ [ENHANCE PROMPT]" in text:
        existing = context_manager.get_scene(user_id)
        if existing:
            await process_and_reply(update, context, existing.raw_user_input)
        else:
            await update.message.reply_text("Отправьте запрос для улучшения, например: «BMW E39 ночью в городе»")
        return
    elif "🚀 [GENERATE]" in text:
        existing = context_manager.get_scene(user_id)
        if existing:
            await update.message.reply_text(
                "🚀 <i>Промпт готов для генерации в панели вашей модели! Скопируйте готовый блок выше.</i>",
                parse_mode=ParseMode.HTML,
            )
        else:
            await update.message.reply_text("Сначала отправьте описание сцены.")
        return

    # Process prompt engineering
    await process_and_reply(update, context, text)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles attached photos with optional captions."""
    if not update.message or not update.message.photo:
        return

    user_id = update.effective_user.id
    caption = update.message.caption or "Сделай ролик на основе этого изображения"
    
    # Analyze with image reference flag enabled
    await process_and_reply(update, context, caption, has_image=True)


async def process_and_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_input: str,
    has_image: bool = False,
    override_mode: ProcessingMode = None,
) -> None:
    user_id = update.effective_user.id
    mode = override_mode or context_manager.get_mode(user_id)
    model = context_manager.get_model(user_id)
    task_type = context_manager.get_task_type(user_id)

    # Show typing / recording action
    await update.effective_chat.send_action("typing")

    # Generate prompt result
    result = prompt_engine.process(
        user_id=user_id,
        user_input=user_input,
        mode=mode,
        model=model,
        task_type=task_type,
        has_image=has_image,
    )

    formatted_text = prompt_engine.format_telegram_output(result)

    # If critical clarifications exist, prepend them
    if result.clarification_questions:
        clarification_msg = "⚠️ <b>Уточнение:</b>\n" + "\n".join(f"• {q}" for q in result.clarification_questions) + "\n\n"
        formatted_text = clarification_msg + formatted_text

    await update.effective_message.reply_text(
        formatted_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_prompt_actions_keyboard(has_director=(mode == ProcessingMode.DIRECTOR)),
    )


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles inline button clicks."""
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = update.effective_user.id

    if data.startswith("set_model:"):
        model_name = data.split(":", 1)[1]
        context_manager.set_model(user_id, model_name)
        await query.edit_message_text(
            f"✅ Модель переключена на <b>{model_name}</b>.",
            parse_mode=ParseMode.HTML,
        )
    elif data.startswith("set_mode:"):
        mode_name = data.split(":", 1)[1]
        new_mode = ProcessingMode(mode_name)
        context_manager.set_mode(user_id, new_mode)
        await query.edit_message_text(
            f"✅ Режим работы переключен на <b>{mode_name}</b>.",
            parse_mode=ParseMode.HTML,
        )
    elif data.startswith("regen:"):
        target_mode = ProcessingMode(data.split(":", 1)[1])
        existing = context_manager.get_scene(user_id)
        if existing:
            await process_and_reply(
                update,
                context,
                existing.raw_user_input,
                has_image=existing.has_reference_image,
                override_mode=target_mode,
            )
        else:
            await query.message.reply_text("Сцена не найдена. Напишите новый запрос.")
    elif data == "open_models":
        current_model = context_manager.get_model(user_id)
        await query.message.reply_text(
            "Выберите модель:",
            reply_markup=get_models_inline_keyboard(current_model),
        )
    elif data == "action_new":
        context_manager.reset_context(user_id)
        await query.message.reply_text(
            "✨ Сцена очищена. Введите новый запрос.",
            reply_markup=get_main_reply_keyboard(),
        )

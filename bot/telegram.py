"""
Main Telegram Bot Application Builder.
Registers commands, sets bot menu, and runs the polling loop.
"""

import logging
from telegram import BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from config.settings import settings
from bot.handlers import (
    start_handler,
    new_scene_handler,
    video_command_handler,
    image_command_handler,
    edit_command_handler,
    models_command_handler,
    settings_command_handler,
    message_handler,
    photo_handler,
    callback_query_handler,
)

logger = logging.getLogger(__name__)


def build_application() -> Application:
    """Builds and configures python-telegram-bot application."""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured! Please provide it in .env.")

    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("new", new_scene_handler))
    app.add_handler(CommandHandler("video", video_command_handler))
    app.add_handler(CommandHandler("image", image_command_handler))
    app.add_handler(CommandHandler("edit", edit_command_handler))
    app.add_handler(CommandHandler("models", models_command_handler))
    app.add_handler(CommandHandler("settings", settings_command_handler))

    # Register message & media handlers
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Register callback queries
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    return app


async def setup_commands(app: Application) -> None:
    """Sets bot commands in Telegram UI menu."""
    commands = [
        BotCommand("start", "Запустить бота и получить инструкцию"),
        BotCommand("new", "Начать новую сцену (очистить контекст)"),
        BotCommand("video", "Режим генерации видео"),
        BotCommand("image", "Режим генерации изображений"),
        BotCommand("edit", "Режим редактирования референса"),
        BotCommand("models", "Выбрать модель (Kling, Veo, Flux, Runway и др.)"),
        BotCommand("settings", "Режимы (FAST / PRO / DIRECTOR)"),
    ]
    try:
        await app.bot.set_my_commands(commands)
    except Exception as e:
        logger.warning(f"Could not set bot commands menu: {e}")


def run_bot() -> None:
    """Starts the bot in long polling mode."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    print("Starting Higgsfield AI Prompt Filter Bot...")
    app = build_application()
    app.post_init = setup_commands
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    run_bot()

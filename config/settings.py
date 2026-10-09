"""
Configuration loader for Higgsfield Prompt Filter.
Securely manages tokens and defaults from environment without leaking them.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)


class Settings:
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    CLOUDFLARE_API_TOKEN: str = os.getenv("CLOUDFLARE_API_TOKEN", "")
    CLOUDFLARE_ACCOUNT_ID: str = os.getenv("CLOUDFLARE_ACCOUNT_ID", "029ee384692df9e11681aad32c1b6db9")
    
    DEFAULT_MODE: str = os.getenv("DEFAULT_MODE", "PRO")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "Kling")
    DEFAULT_TASK_TYPE: str = os.getenv("DEFAULT_TASK_TYPE", "video")

    @classmethod
    def is_configured(cls) -> bool:
        return bool(cls.TELEGRAM_BOT_TOKEN)

    @classmethod
    def get_masked_token(cls, token_name: str) -> str:
        """Returns masked token string safe for logs or status display."""
        val = getattr(cls, token_name, "")
        if not val or len(val) < 8:
            return "***NOT_SET***"
        return f"{val[:4]}...{val[-4:]}"


settings = Settings()

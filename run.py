"""
Entry point to run the Higgsfield AI Prompt Filter Telegram Bot.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from bot.telegram import run_bot

if __name__ == "__main__":
    run_bot()

from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_BOTANIM_CHANNEL_ID = int(os.getenv("TELEGRAM_BOTANIM_CHANNEL_ID", "0"))

POSTGRES_HOST = os.getenv('POSTGRES_HOST', '')
POSTGRES_USER = os.getenv("POSTGRES_USER", '')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
POSTGRES_DB = os.getenv('POSTGRES_DB', '')

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

DATE_FORMAT = "%d.%m.%Y"
ALL_BOOKS_CALLBACK_PATTERN = "all_books_"
VOTE_BOOKS_CALLBACK_PATTERN = "vote_"


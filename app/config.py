from dotenv import load_dotenv
import os

load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_BOTANIM_CHANNEL_ID = int(os.getenv("TELEGRAM_BOTANIM_CHANNEL_ID", "0"))
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '')
POSTGRES_USER = os.getenv("POSTGRES_USER", '')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
POSTGRES_DB = os.getenv('POSTGRES_DB', '')


import logging

from aiogram import Bot, Dispatcher, executor, types
import config
from handlers import message_handlers
from db import DB

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

db = DB()

dp.register_message_handler(message_handlers.start)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)        
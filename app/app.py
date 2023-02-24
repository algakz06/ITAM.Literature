import logging

from aiogram import Bot, Dispatcher, executor, types
import config
from handlers import message_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)


dp.register_message_handler(message_handlers.start)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)        
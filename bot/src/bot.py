from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode

from src import configs

bot = Bot(configs.TOKEN, parse_mode=ParseMode.HTML)

from aiogram.types import BotCommand
from src.utils import fformat


def get_commands() -> list[BotCommand]:
    return [
        BotCommand(command='/start', description=fformat('command.start'))
    ]

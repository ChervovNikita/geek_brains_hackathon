import re

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat
from aiogram.filters import CommandStart, Command, StateFilter

from src.utils import fformat, fill_keys
from src.helpers.command_list import get_commands
from src import keyboards, database as db

from src.bot import bot

router = Router()


@router.message(CommandStart(), ~F.text.contains(' '))
async def start(
        message: types.Message,
        user: db.User,
        state: FSMContext
):
    await state.clear()
    await bot.set_my_commands(get_commands(), scope=BotCommandScopeChat(chat_id=user.id))
    await message.answer(
        fformat("welcome", full_name=user.full_name),
        reply_markup=keyboards.MENU
    )

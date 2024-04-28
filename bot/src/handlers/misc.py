from aiogram import Router, types

from src.utils import fformat

router = Router()


@router.message()
async def misc(message: types.Message):
    await message.answer(fformat("unknown_command"))


@router.callback_query()
async def misc(query: types.CallbackQuery):
    await query.answer(fformat("unknown_button"))

import json
import typing as tp

from pathlib import Path
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from .utils import json_get
from .validators import __validate_json
from .formatter import fformat

KEYBOARDS = json.loads(Path('data/keyboards.json').read_text())


def __identify_keyboard_type(buttons: list[list[str]] | list[list[list[str]]]) -> tp.Optional[str]:
    if not isinstance(buttons, list):
        return None

    inline_type_buttons = False
    reply_type_buttons = False
    for row in buttons:
        if not isinstance(row, list):
            return None
        for button in row:
            reply_type_buttons |= isinstance(button, str)
            inline_type_buttons |= (
                    isinstance(button, list) and len(button) == 2 and
                    isinstance(button[0], str) and isinstance(button[1], str)
            )

    if inline_type_buttons == reply_type_buttons:
        return None

    return 'inline' if inline_type_buttons else 'reply'


def __build_inline_keyboard(buttons: list[list[list[str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=fformat(button[0]), callback_data=button[1])
            for button in row
        ] for row in buttons]
    )


def __build_reply_keyboard(
        buttons: list[list[str]],
        one_time: bool = False
) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=fformat(button)) for button in row] for row in buttons],
        resize_keyboard=True,
        one_time_keyboard=one_time
    )


def __build_keyboard(
        buttons: list[list[str]] | list[list[list[str]]],
        one_time: bool = False
) -> ReplyKeyboardMarkup | InlineKeyboardMarkup | None:
    keyboard_type = __identify_keyboard_type(buttons)
    return (
        None if keyboard_type is None else
        __build_inline_keyboard(buttons) if keyboard_type == 'inline' else
        __build_reply_keyboard(buttons, one_time=one_time)
    )


def get_keyboard(
        keyboard_key: str,
        one_time: bool = False
) -> ReplyKeyboardMarkup | InlineKeyboardMarkup | None:
    buttons = json_get(keyboard_key, KEYBOARDS, allow_list=True)
    return (
        None if buttons is None else
        __build_keyboard(buttons, one_time=one_time)
    )


if errors := __validate_json(KEYBOARDS):
    raise ValueError(f'keyboards.json contains invalid string: "{errors[0]}"')

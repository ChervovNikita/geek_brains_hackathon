import re

from aiogram import Router, types, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat
from aiogram.filters import CommandStart, Command, StateFilter

from src.helpers.courses import (
    get_courses,
    get_course
)
from src.helpers.keyboards import (
    course_list_keyboard,
    course_keyboard,
    lesson_keyboard,
    SelectCourse,
    SelectLesson,
    QuizByLesson,
    QuizByCourse
)
from src.utils import fformat, fill_keys
from src.helpers.command_list import get_commands
from src import keyboards, database as db

from src.bot import bot

router = Router()


@router.callback_query(F.data == "choose_course")
async def course_list(query: types.CallbackQuery):
    await query.answer()
    await query.message.answer(
        fformat("select.course"),
        reply_markup=course_list_keyboard(get_courses())
    )


@router.callback_query(SelectCourse.filter())
async def course_page(
        query: types.CallbackQuery,
        callback_data: SelectCourse
):
    course = get_course(callback_data.course_slug)
    await query.answer()
    await query.message.answer(
        fformat(
            "select.lesson",
            course_name=course.name,
            question_count=course.question_count,
            lesson_count=len(course.lessons)
        ),
        reply_markup=course_keyboard(course)
    )


@router.callback_query(SelectLesson.filter())
async def lesson_page(
        query: types.CallbackQuery,
        callback_data: SelectLesson
):
    course = get_course(callback_data.course_slug)
    lesson = course.lessons[callback_data.lesson_index]

    await query.answer()
    await query.message.answer(
        fformat("select.lesson_selected", lesson_name=lesson.name, question_count=lesson.question_count),
        reply_markup=lesson_keyboard(lesson)
    )

import re

from aiogram import Router, types, F
from aiogram.enums.chat_action import ChatAction
from aiogram import Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat
from aiogram.filters import CommandStart, Command, StateFilter

from src.fsm import QuizByCourseState, QuizByLessonState
from src.helpers.courses import (
    get_courses,
    get_course, Question, Lesson
)
from src.helpers.keyboards import (
    QuizByLesson,
    QuizByCourse
)
from src.model.get_recommendations import get_recommendations
from src.utils import fformat, fill_keys
from src.helpers.command_list import get_commands
from src import keyboards, database as db, configs

router = Router()


def get_question(question_data: dict) -> Question:
    print(question_data)
    course = get_course(question_data["course_slug"])
    lesson = course.lessons[question_data["lesson_index"]]
    return lesson.questions[question_data["question_index"]]


def get_lesson(question_data: dict) -> Lesson:
    print(question_data)
    course = get_course(question_data["course_slug"])
    lesson = course.lessons[question_data["lesson_index"]]
    return lesson


@router.callback_query(QuizByCourse.filter())
async def start_quiz_by_course(
        query: types.CallbackQuery,
        callback_data: QuizByCourse,
        session: db.Session,
        state: FSMContext
):
    course = get_course(callback_data.course_slug)
    questions = course.select_random_questions_indexes()
    question = get_question(questions[0])

    await state.clear()
    await state.set_state(QuizByCourseState.answering)
    await state.update_data(course_slug=course.slug, questions=questions, question_index=0)

    await query.answer()
    await query.message.answer(
        fformat("quiz.course.text", course_name=course.name, question_index=1, question_count=len(questions), question_text=question.text),
    )


@router.callback_query(QuizByLesson.filter())
async def start_quiz_by_lesson(
        query: types.CallbackQuery,
        callback_data: QuizByLesson,
        session: db.Session,
        state: FSMContext
):
    course = get_course(callback_data.course_slug)
    lesson = course.lessons[callback_data.lesson_index]
    questions = lesson.select_random_questions_indexes()
    question = get_question(questions[0])

    await state.clear()
    await state.set_state(QuizByLessonState.answering)
    await state.update_data(
        course_slug=course.slug,
        lesson_index=callback_data.lesson_index,
        questions=questions,
        question_index=0
    )

    await query.answer()
    await query.message.answer(
        fformat("quiz.lesson.text", lesson_name=lesson.name, question_index=1, question_count=len(questions), question_text=question.text),
    )


@router.message(StateFilter(QuizByCourseState.answering))
@router.message(StateFilter(QuizByLessonState.answering))
async def get_course_answer(
        message: types.Message,
        session: db.Session,
        state: FSMContext,
        bot: Bot
):
    data = await state.get_data()
    quiz_by = "lesson" if "lesson_index" in data else "course"

    questions = data["questions"]
    question_index = data["question_index"]

    lesson = get_lesson(questions[question_index])
    question = get_question(questions[question_index])

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    correctness, comment = get_recommendations(question.text, message.text, lesson.slug)
    if correctness == 1:
        text = f"🔥 Правильно!\n\n{comment}"
    else:
        text = f"🫣 Не правильно :(\n\n{comment}"

    questions[question_index]["correctness"] = correctness

    await state.update_data(question_index=question_index + 1, questions=questions)
    if question_index + 1 >= len(questions):
        correct_answer_count = sum(question["correctness"] for question in questions)
        is_good_responses = round(correct_answer_count / len(questions), 2) >= configs.CORRECT_THRESHOLD

        await message.answer(text)
        await state.clear()

        if is_good_responses:
            return await message.answer(
                fformat(
                    f"quiz.{quiz_by}.finish.good",
                    course_name=lesson.course_slug,
                    lesson_name=lesson.name,
                    correct_answer_count=correct_answer_count,
                    question_count=len(questions)
                ),
            )

        recommendations = '\n'.join([
            f"- {get_question(question).text}"
            for question in questions
            if question["correctness"] != 1
        ])

        return await message.answer(
            fformat(
                f"quiz.{quiz_by}.finish.recommendations",
                course_name=lesson.course_slug,
                lesson_name=lesson.name,
                correct_answer_count=correct_answer_count,
                question_count=len(questions),
                recommendations=recommendations
            ),
        )

    question = get_question(questions[question_index + 1])

    await message.answer(text)
    await message.answer(
        fformat(f"quiz.{quiz_by}.text", course_name=lesson.course_slug, lesson_name=lesson.name, question_index=question_index + 2, question_count=len(questions),
                question_text=question.text),
    )

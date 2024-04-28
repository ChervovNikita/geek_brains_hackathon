from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.helpers.courses import Course, Lesson, Question


class QuizByLesson(CallbackData, prefix="quiz"):
    course_slug: str
    lesson_index: int


class QuizByCourse(CallbackData, prefix="quiz"):
    course_slug: str


class SelectCourse(CallbackData, prefix="select"):
    course_slug: str


class SelectLesson(CallbackData, prefix="select"):
    course_slug: str
    lesson_index: int


def course_list_keyboard(courses: list[Course]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(callback_data=SelectCourse(course_slug=course.slug).pack(), text=course.name)]
        for course in courses
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def course_keyboard(course: Course) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(callback_data=SelectLesson(course_slug=course.slug, lesson_index=lesson_index).pack(), text=lesson.name)]
        for lesson_index, lesson in enumerate(course.lessons)
    ]
    buttons.append([InlineKeyboardButton(callback_data=QuizByCourse(course_slug=course.slug).pack(), text="Потренироваться")])
    buttons.append([InlineKeyboardButton(callback_data="choose_course", text="Назад")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def lesson_keyboard(lesson: Lesson) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(callback_data=QuizByLesson(course_slug=lesson.course_slug, lesson_index=lesson.index).pack(), text="Потренироваться")],
        [InlineKeyboardButton(callback_data=SelectCourse(course_slug=lesson.course_slug).pack(), text="Назад")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

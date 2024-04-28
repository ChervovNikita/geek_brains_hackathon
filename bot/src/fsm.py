from aiogram.fsm.state import State, StatesGroup


class QuizByCourseState(StatesGroup):
    answering = State()


class QuizByLessonState(StatesGroup):
    answering = State()

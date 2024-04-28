import itertools
import json
import random as rnd
from pathlib import Path

from dataclasses import dataclass


@dataclass
class Question:
    text: str
    answer: str
    comment: str | None


@dataclass
class Lesson:
    course_slug: str
    name: str
    index: int
    questions: list[Question]

    def select_random_questions_indexes(self, k: int | None = None) -> list[dict]:
        question_indexes = [
            {
                "question_index": i,
                "lesson_index": self.index,
                "course_slug": self.course_slug
            }
            for i, question in enumerate(self.questions)
        ]

        k = k or min(len(question_indexes), rnd.randint(5, 10))
        return rnd.sample(question_indexes, k)

    @property
    def question_count(self) -> int:
        return len(self.questions)

    @property
    def slug(self) -> str:
        return f"{self.course_slug}_{self.index + 1}"


@dataclass
class Course:
    name: str
    slug: str
    lessons: list[Lesson]

    @property
    def question_count(self) -> int:
        return sum(lesson.question_count for lesson in self.lessons)

    def select_random_questions_indexes(self, k: int | None = None) -> list[dict]:
        question_indexes = list(itertools.chain(*[[
            {
                "question_index": i,
                "lesson_index": lesson.index,
                "course_slug": self.slug
            }
            for i, question in enumerate(lesson.questions)] for lesson in self.lessons
        ]))
        k = k or min(len(question_indexes), rnd.randint(5, 10))
        return rnd.sample(question_indexes, k)


__courses_raw = json.loads(Path("data/courses.json").read_text())
COURSES = {
    course_slug: Course(
        name=course["name"],
        slug=course_slug,
        lessons=[
            Lesson(
                course_slug=course_slug,
                name=lesson["name"],
                index=lesson_index,
                questions=[
                    Question(
                        text=question["question"],
                        answer=question["answer"],
                        comment=question["comment"]
                    )
                    for question in lesson["questions"]
                ]
            )
            for lesson_index, lesson in enumerate(course["lessons"])
        ]
    )
    for course_slug, course in __courses_raw.items()
}
LIGHT_COURSES = sorted([
    Course(
        name=course.name,
        slug=course.slug,
        lessons=[]
    )
    for course in COURSES.values()
], key=lambda c: c.slug)


def get_courses() -> list[Course]:
    return LIGHT_COURSES


def get_course(course_slug: str) -> Course:
    return COURSES[course_slug]

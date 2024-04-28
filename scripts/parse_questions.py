import json

import pandas
from pathlib import Path

df = pandas.read_csv("train_data.csv")
df.columns = df.columns.str.lower()

df = df.map(lambda x: x.strip() if isinstance(x, str) else x, na_action="ignore")

corr_ans = df.query("correctness == 1").drop(["correctness"], axis=1)
corr_ans = corr_ans.drop_duplicates(subset=["question"])

questions = corr_ans.to_dict(orient="records")

courses = {}

for i, question in enumerate(questions):
    course = question["lesson"][:question["lesson"].rfind("_")]
    lesson = int(question["lesson"][question["lesson"].rfind("_") + 1:])

    question_comment = None if str(question["comment"]) == "nan" else question["comment"]

    courses.setdefault(course, {
        "name": None,
        "lessons": {}
    })["lessons"].setdefault(lesson, {
        "name": None,
        "questions": []
    })["questions"].append(
        {
            "question": question["question"],
            "answer": question["answer"],
            "comment": question_comment
        }
    )

for course in courses.values():
    course["lessons"] = [
        {
            **lesson,
            "code": lesson_code
        }
        for lesson_code, lesson in course["lessons"].items()
    ]
    course["lessons"].sort(key=lambda l: l["code"])

Path("courses.json").write_text(json.dumps(courses, ensure_ascii=False, indent=2))

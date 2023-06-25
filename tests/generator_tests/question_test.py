from __future__ import annotations

import random
from pathlib import Path

import pytest

from checkmark.generator.question import read_questions_from_excel, select_questions


def test_read_questions_from_excel(temp_excel_path: Path) -> None:
    questions = read_questions_from_excel(str(temp_excel_path / "correct.xlsx"))
    assert len(questions) == 3
    assert questions[0].index == 1
    assert questions[0].body == "Kérdés 1"
    assert questions[0].options == ["A1", "B1", "C1", "D1"]
    assert questions[0].correct == 0


@pytest.mark.parametrize(
    "random_questions, random_option_order, expected_questions, expected_option_order_for_first_question",
    [
        (False, False, [1, 2, 3], ["A1", "B1", "C1", "D1"]),
        (False, True, [1, 2, 3], ["C1", "A1", "B1", "D1"]),
        (True, False, [2, 3, 1], ["A2", "B2", "C2", "D2"]),
        (True, True, [2, 3, 1], ["A2", "B2", "D2", "C2"]),
    ],
)
def test_select_questions(
    temp_excel_path: Path,
    random_questions: bool,
    random_option_order: bool,
    expected_questions: list[int],
    expected_option_order_for_first_question: list[str],
) -> None:
    questions = read_questions_from_excel(str(temp_excel_path / "correct.xlsx"))
    random.seed(0)
    selected_questions = select_questions(
        questions,
        3,
        random_questions,
        random_option_order,
    )
    assert len(selected_questions) == 3
    assert [q.index for q in selected_questions] == expected_questions
    assert selected_questions[0].options == expected_option_order_for_first_question


def test_is_question_valid(temp_excel_path: Path) -> None:
    with pytest.raises(KeyError):
        read_questions_from_excel(str(temp_excel_path / "reoccurring_index.xlsx"))

    with pytest.raises(ValueError):
        read_questions_from_excel(str(temp_excel_path / "unexpected_correct_value.xlsx"))


def test_qestion_repr(temp_excel_path: Path) -> None:
    question = read_questions_from_excel(str(temp_excel_path / "correct.xlsx"))[0]
    print(repr(question))
    assert (
        repr(question)
        == "Question(index=1, body=Kérdés 1, options=['A1', 'B1', 'C1', 'D1'], correct=0)"
    )

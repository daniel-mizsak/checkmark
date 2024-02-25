"""
Question class and related functions.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import copy
import random

import pandas as pd


class Question:
    """Question class to store the data of each question in an assessment."""

    def __init__(self: Question, index: int, body: str, options: list[str], correct: int) -> None:
        """Initializes the Question object.

        Args:
            self (Question): The Question object.
            index (int): The index of the question.
            body (str): The body of the question.
            options (list[str]): The options of the question.
            correct (int): The index of the correct answer.
        """
        self.index = index
        self.body = body
        self.options = options
        self.correct = correct

        self.shuffle_index_list = list(range(len(self.options)))

    def is_question_valid(self: Question, questions: list[Question]) -> bool:
        """Validates the question to ensure that each question has a unique index and a valid correct answer.

        Args:
            questions (list[Question]): Already validated questions.

        Raises:
            KeyError: If multiple questions have the same index raise KeyError.
            ValueError: If the correct answer is not A, B, C or D raise ValueError.

        Returns:
            bool: True if the question is valid.
        """
        if self.index in [q.index for q in questions]:
            msg = f"Több {self.index} számú kérdés van az Excel táblában."
            raise KeyError(msg)
        if self.correct not in range(4):
            msg = f"A {self.index} számú kérdés megoldása nem A, B, C vagy D."
            raise ValueError(msg)
        return True

    def shuffled(self: Question) -> Question:
        """Shuffles the options of the question and returns a new Question object."""
        shuffled = copy.deepcopy(self)
        random.shuffle(self.shuffle_index_list)
        shuffled.correct = self.shuffle_index_list.index(shuffled.correct)
        shuffled.options = [self.options[index] for index in self.shuffle_index_list]
        return shuffled

    def __repr__(self: Question) -> str:
        """Returns a string representation of the question."""
        return (
            f"Question(index={self.index}, "
            f"body={self.body}, "
            f"options={self.options}, "
            f"correct={self.correct})"
        )


def read_questions_from_excel(path: str) -> list[Question]:
    """Reads questions from an Excel file.

    Args:
        path (str): Path to the Excel file.

    Returns:
        list[Question]: List of read questions.
    """
    # TODO: Read questions from other sources like Google Sheets
    questions: list[Question] = []

    source_questions = pd.read_excel(path, dtype="str")
    for _, source_question in source_questions.iterrows():
        index = source_question["Feladat sorszám"]
        body = source_question["Kérdés"]
        options = [source_question[q] for q in "ABCD"]
        correct = ord(source_question["Megoldás"].upper()) - ord("A")

        question = Question(int(index), str(body), list(options), int(correct))
        if question.is_question_valid(questions):
            questions.append(question)
    return questions


def select_questions(
    all_questions: list[Question],
    question_number: int,
    random_questions: bool,  # noqa: FBT001
    random_option_order: bool,  # noqa: FBT001
) -> list[Question]:
    """Select a subset of questions from the list of all questions.

    Args:
        all_questions (list[Question]): List of all questions available.
        question_number (int, optional): Number of questions to select. Defaults to 1.
        random_questions (bool, optional): Whether to select questions randomly. Defaults to False.
        random_option_order (bool, optional): Whether to shuffle the options of the questions.
        Defaults to False.

    Returns:
        list[Question]: List of selected questions.
    """
    if random_questions:
        selected_indices = random.sample(list(range(len(all_questions))), k=question_number)
    else:
        selected_indices = list(range(question_number))

    if random_option_order:
        return [all_questions[index].shuffled() for index in selected_indices]
    return [all_questions[index] for index in selected_indices]

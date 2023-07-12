"""
Assessment generating and logging functionalities.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import random
import string
from dataclasses import asdict, dataclass
from textwrap import dedent

import requests

from checkmark.generator.pdf import PDFData, create_pdf
from checkmark.generator.question import read_questions_from_excel, select_questions


@dataclass
class CheckmarkFields:
    """Data necessary data for the checkmark generator. These fields are given in the GUI."""

    class_: str
    subject: str
    topic: str
    students: list[str]
    online_evaluator: bool
    date: str
    question_number: int
    random_question_order: bool
    random_option_order: bool


@dataclass
class PocketData:
    """Data necessary for the checkmark online evaluation pocket. This info is sent to the server"""

    students: list[str]
    date: str
    pocket_id: str
    pocket_password: str


def generate_assessment(checkmark_fields: CheckmarkFields) -> bool:
    """Generates, saves and logs assessments.

    Args:
        checkmark_fields (CheckmarkFields): Data necessary for checkmark generator.

    Returns:
        bool: True if the assessments were generated successfully, False otherwise.
    """
    logger = setup_logger(__name__)
    pdf_path = (
        "data/generated/"
        + f"{checkmark_fields.date}_{checkmark_fields.subject}_{checkmark_fields.class_}"
    )
    os.makedirs(pdf_path, exist_ok=True)

    class_number = checkmark_fields.class_.split("-")[0]
    topic_path = checkmark_fields.topic.replace(" ", "_").replace(".", "") + ".xlsx"
    questions_path = f"data/assessments/{checkmark_fields.subject}-{class_number}/{topic_path}"
    all_questions = read_questions_from_excel(questions_path)

    pocket_data = generate_pocket_data(checkmark_fields.students, checkmark_fields.date)
    with open(f"{pdf_path}/pocket_data.json", "w", encoding="utf-8") as file_handle:
        json.dump(asdict(pocket_data), file_handle, indent=4, ensure_ascii=False)

    if checkmark_fields.online_evaluator:
        if not send_pocket_data(pocket_data):
            return False

    for student in checkmark_fields.students:
        random.seed()
        questions = select_questions(
            all_questions,
            checkmark_fields.question_number,
            checkmark_fields.random_question_order,
            checkmark_fields.random_option_order,
        )

        pdf_data = PDFData(
            student,
            checkmark_fields.class_,
            checkmark_fields.subject,
            checkmark_fields.topic,
            checkmark_fields.date,
            questions,
            pocket_data.pocket_id,
            pocket_data.pocket_password,
        )

        pdf = create_pdf(pdf_data)
        pdf_name = f"{pdf_path}/{checkmark_fields.topic.replace('.', '')}_{student}.pdf".replace(
            " ", "_"
        )
        pdf.output(pdf_name)

        log_data(pdf_data, logger)

    # TODO: Add document printing functionality
    # https://stackoverflow.com/questions/27195594/python-silent-print-pdf-to-specific-printer
    return True


def setup_logger(logger_name: str) -> logging.Logger:
    """Setting up the logger for the checkmark generator.

    Args:
        logger_name (str):

    Returns:
        logging.Logger: _description_
    """
    log_path = "data/app/"
    os.makedirs(log_path, exist_ok=True)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s:%(asctime)s:\n%(message)s\n")
    file_hanfler = logging.FileHandler(log_path + "checkmark.log", encoding="utf-8")
    file_hanfler.setFormatter(formatter)
    logger.addHandler(file_hanfler)

    # Disable warning: "FFTM NOT subset; don't know how to subset; dropped" from fontTools
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    return logger


def log_data(pdf_data: PDFData, logger: logging.Logger) -> None:
    """Save logged data."""
    log_text = dedent(
        f"""\
        Pocket: {pdf_data.pocket_id}
        Name: {pdf_data.student}
        Class: {pdf_data.class_}
        Subject: {pdf_data.subject}
        Topic: {pdf_data.topic}
        Date: {pdf_data.date}
        Questions:
    """
    )
    for question_number, question in enumerate(pdf_data.questions):
        log_text += f"{question_number + 1}: {question}\n"
    logger.info(log_text)


def generate_pocket_data(students: list[str], date: str) -> PocketData:
    """Generates and saves pocket data from evaluation.

    Args:
        students (list[str]): The name of students we expect solutions from.
        date (str): The date of the assessment generation.
    """
    letters = string.ascii_uppercase
    current_time = datetime.datetime.now().strftime("%y%m%d%H%M%S%f")
    pocket_id = "".join(random.choice(letters) for _ in range(2))
    pocket_id = current_time + pocket_id
    pocket_pw = "".join(random.choice(letters) for _ in range(8))
    pocket_data = PocketData(students, date, pocket_id, pocket_pw)
    return pocket_data


def send_pocket_data(pocket_data: PocketData) -> bool:
    """Send pocket data to the server."""
    data_json = json.dumps(asdict(pocket_data))
    try:
        response = requests.post(
            "http://127.0.0.1:5000/checkmark/create-pocket/",
            json=data_json,
            timeout=5,
        ).json()
        if response.status_code != 200:
            return False
    except requests.exceptions.ConnectionError:
        return False
    return True

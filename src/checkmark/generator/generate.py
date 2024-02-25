"""
Assessment generating and logging functionalities.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import json
import logging
import random
import string
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from textwrap import dedent

import requests

from checkmark import BASE_URL, REGISTER_POCKET_ENDPOINT
from checkmark.generator.pdf import PDFData, create_pdf
from checkmark.generator.question import read_questions_from_excel, select_questions


@dataclass
class CheckmarkFields:
    """Data for the checkmark generator. These fields are loaded in the GUI."""

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
    """Data for the online evaluation pocket. This info is sent to the server."""

    students: list[str]
    date: str
    pocket_id: str
    pocket_password: str


def generate_assessment(checkmark_fields: CheckmarkFields) -> bool:
    """Manages and logs assessment generation.

    Args:
        checkmark_fields (CheckmarkFields): Data necessary for checkmark generator.

    Returns:
        bool: True if the assessments were generated successfully, False otherwise.
    """
    logger = _setup_logger(__name__)
    pdf_path = f"data/generated/{checkmark_fields.date}_{checkmark_fields.subject}_{checkmark_fields.class_}"
    Path(pdf_path).mkdir(parents=True, exist_ok=True)

    class_number = checkmark_fields.class_.split("-")[0]
    topic_path = checkmark_fields.topic.replace(" ", "_").replace(".", "") + ".xlsx"
    questions_path = f"data/assessments/{checkmark_fields.subject}-{class_number}/{topic_path}"
    all_questions = read_questions_from_excel(questions_path)

    pocket_data = _generate_pocket_data(checkmark_fields.students, checkmark_fields.date)
    with Path(f"{pdf_path}/pocket_data.json").open("w", encoding="utf-8") as file_handle:
        json.dump(asdict(pocket_data), file_handle, indent=4, ensure_ascii=False)

    if checkmark_fields.online_evaluator and not _send_pocket_data(pocket_data):
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
        pdf_name = f"{pdf_path}/{checkmark_fields.topic.replace('.', '')}_{student}.pdf"
        pdf_name = pdf_name.replace(" ", "_")
        pdf.output(pdf_name)

        _log_data(pdf_data, logger)

    # TODO: Add document printing functionality
    # https://stackoverflow.com/questions/27195594/python-silent-print-pdf-to-specific-printer
    return True


def _setup_logger(logger_name: str) -> logging.Logger:
    """Setting up the logger for the checkmark generator."""
    log_path = "data/app/"
    Path(log_path).mkdir(exist_ok=True)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s:%(asctime)s:\n%(message)s\n")
    file_handler = logging.FileHandler(log_path + "checkmark.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Disable warning: "FFTM NOT subset; don't know how to subset; dropped" from fontTools
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    return logger


def _log_data(pdf_data: PDFData, logger: logging.Logger) -> None:
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
    """,
    )
    for question_number, question in enumerate(pdf_data.questions):
        log_text += f"{question_number + 1}: {question}\n"
    logger.info(log_text)


def _generate_pocket_data(students: list[str], date: str) -> PocketData:
    """Generates and saves pocket data from evaluation."""
    letters = string.ascii_uppercase
    current_time = datetime.now().strftime("%y%m%d%H%M%S%f")  # noqa: DTZ005
    pocket_id = "".join(random.choice(letters) for _ in range(2))  # noqa: S311
    pocket_id = current_time + pocket_id
    pocket_password = "".join(random.choice(letters) for _ in range(8))  # noqa: S311
    return PocketData(students, date, pocket_id, pocket_password)


def _send_pocket_data(pocket_data: PocketData) -> bool:
    """Send pocket data to the server."""
    target_url = BASE_URL + REGISTER_POCKET_ENDPOINT
    ok_response = 200
    data_json = json.dumps(asdict(pocket_data))
    try:
        response = requests.post(url=target_url, json=data_json, timeout=5).json()
        if response.status_code != ok_response:
            return False
    except requests.exceptions.ConnectionError:
        return False
    return True

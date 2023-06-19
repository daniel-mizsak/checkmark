import argparse
import json
import logging
import os
import random
import string
from textwrap import dedent

import requests

from checkmark.generator.pdf import create_pdf
from checkmark.generator.question import (
    Question,
    read_questions_from_excel,
    select_questions,
)


def generate_assessment(
    osztaly: str,
    tantargy: str,
    temakor: str,
    tanulok: list[str],
    email: str,
    online_kiertekeles: bool,
    datum: str,
    kerdesek_szama: int,
    veletlenszeru_kerdesek: bool,
    veletlenszeru_valaszok: bool,
) -> int:
    logger = setup_logger(__name__)

    class_number = osztaly.split("-")[0]
    topic_path = temakor.replace(" ", "_").replace(".", "") + ".xlsx"
    questions_path = f"data/assessments/{tantargy}-{class_number}/{topic_path}"
    all_questions = read_questions_from_excel(questions_path)

    password = load_password()
    pocket_id = get_pocket_id(tanulok, email, datum, password) if online_kiertekeles else ""

    for student in tanulok:
        random.seed()
        questions = select_questions(
            all_questions,
            kerdesek_szama,
            veletlenszeru_kerdesek,
            veletlenszeru_valaszok,
        )
        create_pdf(
            student,
            osztaly,
            tantargy,
            temakor,
            datum,
            questions,
            pocket_id,
        )
        log_data(
            student,
            osztaly,
            tantargy,
            temakor,
            datum,
            questions,
            pocket_id,
            logger,
        )

    return 0

    # TODO: Add document printing functionality
    # https://stackoverflow.com/questions/27195594/python-silent-print-pdf-to-specific-printer


def setup_logger(logger_name: str) -> logging.Logger:
    log_path = f"data/app_data/"
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


def log_data(
    student: str,
    class_: str,
    subject_: str,
    topic_: str,
    date: str,
    questions: list[Question],
    pocket_id: str | None,
    logger: logging.Logger,
) -> None:
    log_text = dedent(
        f"""\
        Pocket: {pocket_id}
        Name: {student}
        Class: {class_}
        Subject: {subject_}
        Topic: {topic_}
        Date: {date}
        Questions:
    """
    )
    for question_number, question in enumerate(questions):
        log_text += f"{question_number + 1}: {question}\n"
    logger.info(log_text)


def load_password() -> str:
    # TODO: Better coherence with load_email() and check if password is empty
    password_path = "data/app_data/data.json"
    try:
        with open(password_path, "r", encoding="utf-8") as f:
            password = json.loads(f.read())["password"]
    except FileNotFoundError:
        letters = string.ascii_uppercase
        password = "".join(random.choice(letters) for _ in range(16))
        with open(password_path, "r+", encoding="utf-8") as f:
            data = json.loads(f.read())
            data["password"] = password
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4, ensure_ascii=False)
    return password


def get_pocket_id(students: list[str], email: str, date: str, password: str) -> str:
    data = json.dumps(
        {
            "email": email,
            "students": students,
            "date": date,
            "password": password,
        }
    )
    try:
        response = requests.post(
            "http://127.0.0.1:5000/checkmark/create-pocket/",
            json=data,
            timeout=5,
        ).json()
        pocket_id = response["pocket_id"]
    except requests.exceptions.ConnectionError:
        pocket_id = ""
    return pocket_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--osztaly",
        type=str,
        help="Osztály",
        required=True,
    )
    parser.add_argument(
        "-tt",
        "--tantargy",
        type=str,
        help="Tantárgy",
        required=True,
    )
    parser.add_argument(
        "-tk",
        "--temakor",
        type=str,
        help="Témakör",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--tanulok",
        type=str,
        action="append",
        help="Tanulók",
        required=True,
    )
    parser.add_argument(
        "-e",
        "--email",
        type=str,
        help="Email",
        required=True,
    )
    parser.add_argument(
        "-ok",
        "--online_kiertekeles",
        default=False,
        type=str,
        help="Online kiértékelés",
        required=False,
    )
    parser.add_argument(
        "-d",
        "--datum",
        type=str,
        help="Dátum",
        required=True,
    )
    parser.add_argument(
        "-ks",
        "--kerdesek_szama",
        type=int,
        help="Kérdések száma",
        required=True,
    )
    parser.add_argument(
        "-vk",
        "--veletlenszeru_kerdesek",
        default=False,
        type=bool,
        help="Véletlenszerű kérdések",
        required=False,
    )
    parser.add_argument(
        "-vv",
        "--veletlenszeru_valaszok",
        default=False,
        type=bool,
        help="Véletlenszerű válaszok",
        required=False,
    )

    args = parser.parse_args()
    for arg in vars(args):
        if getattr(args, arg) is None:
            parser.error(f"Missing argument: {arg}")

    raise SystemExit(
        generate_assessment(
            args.osztaly,
            args.tantargy,
            args.temakor,
            args.tanulok,
            args.email,
            args.online_kiertekeles,
            args.datum,
            args.kerdesek_szama,
            args.veletlenszeru_kerdesek,
            args.veletlenszeru_valaszok,
        )
    )

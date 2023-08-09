from __future__ import annotations

import datetime
import os
import random
import smtplib
import string
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import dotenv_values


@dataclass
class Pocket:
    email: str
    students: list[str]
    date: str
    password: str
    pocket_id: str
    pocket_pw: str
    results: dict[str, str] = field(default_factory=dict)


def generate_pocket_id() -> str:
    letters = string.ascii_uppercase
    current_time = datetime.datetime.now().strftime("%Y%m%d")
    pocket_id = "".join(random.choice(letters) for _ in range(2))
    pocket_id = current_time + pocket_id
    return pocket_id


def generate_pocket_password() -> str:
    letters = string.ascii_uppercase
    pocket_pw = "".join(random.choice(letters) for _ in range(8))
    return pocket_pw


def send_email(data: Pocket) -> None:
    config = dotenv_values(".env")
    if not config:
        config = dict(os.environ)
    try:
        EMAIL_ADDRESS = config["EMAIL_ADDRESS"]
        EMAIL_PASSWORD = config["EMAIL_PASSWORD"]
    except KeyError as e:
        raise KeyError(
            "Config variables are missing. Check .env file or add environment variables."
        ) from e

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Checkmark generated assessment"
    msg["To"] = data.email
    msg["From"] = EMAIL_ADDRESS

    msg_body = f"""
    Your pocket has been created for the date: {data.date}
    To access the results of the assessment, please visit the following link:

    http://192.168.1.80:5000/checkmark/pocket/{data.pocket_id}
    https://pythonvilag.hu/checkmark/pocket/{data.pocket_id}/{data.pocket_pw}

    Students selected for this assessment:
    {', '.join(data.students)}
    """
    msg_text = MIMEText(msg_body, "plain")
    msg.attach(msg_text)

    with smtplib.SMTP_SSL("mail.pythonvilag.hu", 465) as smtp:
        smtp.login(str(EMAIL_ADDRESS), str(EMAIL_PASSWORD))
        smtp.send_message(msg)

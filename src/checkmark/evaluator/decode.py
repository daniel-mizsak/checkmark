from __future__ import annotations

import base64
import json
import random
import sys

import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import Image
from pyzbar import pyzbar


def decode_solution_data(
    qr_img: Image.Image, password: str | None = None
) -> tuple[str, str, list[int], list[int]]:
    if password is None:
        with open("data/app_data/data.json", "r", encoding="utf-8") as file_handle:
            password = json.loads(file_handle.read())["password"]
    random.seed(0)
    salt = random.getrandbits(128).to_bytes(16, sys.byteorder)
    kdf = PBKDF2HMAC(algorithm=SHA256(), length=32, salt=salt, iterations=1)
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

    qr_array = np.array(qr_img, dtype=np.uint8)
    token = pyzbar.decode(qr_array)[0].data
    fernet = Fernet(key)
    secret_message = fernet.decrypt(token).decode()

    student, date, joined_question_data, joined_correct_data = secret_message.split("; ")
    question_data = [int(index) for index in joined_question_data.split(" ")]
    correct_data = [int(correct) for correct in joined_correct_data.split(" ")]

    return student, date, question_data, correct_data

from __future__ import annotations

import json
import os
import sys
import threading
from pathlib import Path

import cv2
from flask import Blueprint, redirect, render_template, request
from werkzeug.utils import secure_filename

from checkmark.evaluator.evaluate import evaluate_assessment
from checkmark.server.pocket import (
    Pocket,
    generate_pocket_id,
    generate_pocket_password,
    send_email,
)

checkmark_page = Blueprint("checkmark_page", __name__, template_folder="templates")
available_pockets: list[Pocket] = []


@checkmark_page.route("/create-pocket/", methods=["GET", "POST"])
def create_pocket() -> str:
    if request.method == "POST":
        jsondata = str(request.get_json())
        data = json.loads(jsondata)
        pocket = Pocket(
            email=data["email"],
            students=data["students"],
            date=data["date"],
            password=data["password"],
            pocket_id=generate_pocket_id(),
            pocket_pw=generate_pocket_password(),
        )
        available_pockets.append(pocket)

        threading.Thread(target=send_email, args=([pocket])).start()
        return json.dumps({"pocket_id": pocket.pocket_id})
    return ""


@checkmark_page.route("/pocket/<pocket_id>/", methods=["GET", "POST"])
def upload_file(pocket_id):
    if pocket_id not in [pocket.pocket_id for pocket in available_pockets]:
        return redirect("/")

    pocket = [pocket for pocket in available_pockets if pocket.pocket_id == pocket_id][0]
    if request.method != "POST":
        return render_template("post/project/checkmark/upload_assessment.html", date=pocket.date)

    if "file" not in request.files:
        return redirect(request.url)
    file = request.files["file"]

    if file.filename in ["", None] or not allowed_file(str(file.filename)):
        return redirect(request.url)

    filename = secure_filename(str(file.filename))
    folder_path = os.path.join(sys.path[0], f"pythonvilag_website/static/uploads/{pocket_id}")
    os.makedirs(folder_path, exist_ok=True)
    file_path = Path(os.path.join(folder_path, filename))

    file.save(file_path)

    student, date, result, corrected_image = evaluate_assessment(
        file_path,
        pocket.password,
    )
    pocket.results[student] = result

    corrected_image_path = file_path.with_name(file_path.stem + "_corrected" + file_path.suffix)
    cv2.imwrite(str(corrected_image_path), corrected_image)

    corrected_image_path = "/".join(corrected_image_path.parts[-3:])

    return render_template(
        "post/project/checkmark/assessment_results.html",
        pocket_id=pocket_id,
        student=student,
        date=date,
        result=result,
        corrected_image_path=corrected_image_path,
    )


def allowed_file(filename: str) -> bool:
    allowed_extensions = {"heic", "jpeg", "jpg", "png"}
    file_extension = filename.rsplit(".", 1)[1].lower()
    return "." in filename and file_extension in allowed_extensions


@checkmark_page.route("/pocket/<pocket_id>/<pocket_pw>/", methods=["GET", "POST"])
def pocket_results(pocket_id, pocket_pw):
    if pocket_id in [pocket.pocket_id for pocket in available_pockets]:
        pocket = [pocket for pocket in available_pockets if pocket.pocket_id == pocket_id][0]
        if pocket.pocket_pw == pocket_pw:
            return pocket.results
    return "no pocket results"

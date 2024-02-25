"""
Server side route and evaluation management.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import cv2
from flask import Blueprint, Response, abort, make_response, redirect, render_template, request
from werkzeug.utils import secure_filename

from checkmark import REGISTER_POCKET_ENDPOINT
from checkmark.evaluator.evaluate import evaluate_assessment

CHECKMARK_CONTENT_PATH = Path(sys.path[0]) / Path("pythonvilag_website/static/modules/checkmark")
checkmark_page = Blueprint("checkmark_page", __name__, template_folder="templates")


@checkmark_page.route(REGISTER_POCKET_ENDPOINT, methods=["GET", "POST"])
def register_pocket() -> Response:
    """Save pocket data on the server side in a json file."""
    if request.method == "POST":
        jsondata = str(request.get_json())
        pocket_data = json.loads(jsondata)

        pocket_id = pocket_data["pocket_id"]
        if not _is_valid_pocket_id(pocket_id):
            return make_response("Invalid pocket ID", 400)

        pocket_path = CHECKMARK_CONTENT_PATH / Path(pocket_id)
        pocket_path.mkdir(exist_ok=True)
        with (pocket_path / Path("pocket_data.json")).open("w", encoding="utf-8") as file_handle:
            json.dump(pocket_data, file_handle, indent=4, ensure_ascii=False)

    return make_response("Success", 200)


def _is_valid_pocket_id(pocket_id: str) -> bool:
    """Check if the pocket ID is valid."""
    pattern = r"^\d{18}[A-Z]{2}$"
    return bool(re.match(pattern, pocket_id))


@checkmark_page.route("/pocket/<pocket_id>/", methods=["GET", "POST"])
def upload_file(pocket_id: str) -> str | Response:
    """Upload assessment to the server and evaluate it."""
    available_pockets = os.listdir(CHECKMARK_CONTENT_PATH)
    if pocket_id not in available_pockets:
        return abort(404)

    pocket_path = CHECKMARK_CONTENT_PATH / Path(pocket_id)
    with (pocket_path / Path("pocket_data.json")).open("r", encoding="utf-8") as file_handle:
        pocket_data = json.load(file_handle)

    if request.method != "POST":
        return render_template("post/project/checkmark/upload_assessment.html", date=pocket_data["date"])

    if "file" not in request.files:
        return redirect(request.url)
    file = request.files["file"]

    if file.filename in ["", None] or not _is_allowed_filetype(str(file.filename)):
        return redirect(request.url)

    filename = secure_filename(str(file.filename))
    file_path = Path(os.path.join(folder_path, pocket_id, filename))
    file.save(file_path)

    result = evaluate_assessment(file_path, pocket_data["pocket_password"])
    # TODO: Figure out final result structure
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


def _is_allowed_filetype(filename: str) -> bool:
    """Check if the extension is among the predefined image extensions."""
    if "." not in filename:
        return False
    allowed_extensions = {"heic", "jpeg", "jpg", "png"}
    file_extension = filename.rsplit(".", 1)[1].lower()
    return file_extension in allowed_extensions


@checkmark_page.route("/pocket/<pocket_id>/<pocket_password>/", methods=["GET", "POST"])
def pocket_results(pocket_id, pocket_password):
    folder_path = os.path.join(sys.path[0], "pythonvilag_website/static/checkmark")
    available_pockets = os.listdir(folder_path)
    if pocket_id not in available_pockets:
        return abort(404)

    with open(f"{folder_path}/{pocket_id}/pocket_data.json", "r", encoding="utf-8") as file_handle:
        pocket_data = json.load(file_handle)

    if pocket_password != pocket_data["pocket_password"]:
        return abort(403)

    return pocket.results

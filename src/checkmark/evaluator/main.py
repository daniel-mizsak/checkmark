from __future__ import annotations

from pathlib import Path

import cv2
from decode import decode_solution_data
from evaluate import evaluate_assessment, load_image


def main(image_path, password=None):
    image = load_image(image_path)
    student, date, question_date, correct_data = decode_solution_data(image, password)
    score, result_image = evaluate_assessment(image, correct_data)
    return student, date, score, result_image

if __name__=='__main__':
    image_path = Path("data/uploads/hi2.jpg")
    student, date, score, result_image = main(image_path)
    cv2.imshow('result image', result_image)
    cv2.waitKey(0)    cv2.waitKey(0)
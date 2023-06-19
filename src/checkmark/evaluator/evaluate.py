
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from pillow_heif import register_heif_opener


def evaluate_assessment(
    image_or_path: Path | Image.Image, correct_answers=None, password: str | None = None
) -> tuple[str, str, str, np.ndarray]:
    big_image = load_image(image_or_path)
    image = cv2.resize(big_image, (1200, 800))
    image_canny = preprocess_image(image)
    contours = get_contours(image_canny)

    ##get_warped_images and get_answers replaced by x_marks_the_spot
    # warped_images = get_warped_images(image.shape[1], image.shape[0], contours, image, threshold1=threshold)
    # given_answers = get_answers(warped_images)
    warped_images, given_answers = x_marks_the_spot(image, contours, correct_answers)

    score, corrected_images = grade_test(warped_images, correct_answers, given_answers)

    result_image = get_inverse_warped_images(
        image.shape[1], image.shape[0], contours, image, corrected_images
    )
    return score, result_image


def load_image(image_path: Path | Image.Image):
    if isinstance(image_path, np.ndarray): return image_path
    if image_path.suffix.lower() == ".heic":
        register_heif_opener()

    image = Image.open(image_path)
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    return image


def preprocess_image(image):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_blur = cv2.GaussianBlur(image_gray, (15, 15), 1)
    image_canny = cv2.Canny(image_blur, 10, 70)
    return image_canny


def get_contours(image_canny):
    contours, hierarchy = cv2.findContours(
        image=image_canny,
        mode=cv2.RETR_TREE,
        method=cv2.CHAIN_APPROX_NONE,
    )
    total_area = image_canny.shape[0] * image_canny.shape[1]

    filtered_contours = []
    hierarchy = hierarchy[0]
    for current_contour, current_hierarchy in zip(contours, hierarchy):
        parent_id = current_hierarchy[3]
        parent = contours[parent_id] if parent_id != -1 else None
        if filter_contour_hierarchy(current_contour, parent, total_area):
            perimeter = cv2.arcLength(current_contour, closed=True)
            approximated_curves = cv2.approxPolyDP(
                current_contour,
                epsilon=0.02 * perimeter,
                closed=True,
            )
            if len(approximated_curves) == 4:
                filtered_contours.append(approximated_curves)

    filtered_contours = sorted(filtered_contours, key=cv2.contourArea, reverse=True)

    ordered_contours = order_contours(filtered_contours)
    return ordered_contours


def filter_contour_hierarchy(current_contour, parent, total_area):
    # TODO: Ensure that these conditions are correct for a wide range of images

    area = cv2.contourArea(current_contour)
    # area_condition
    if not (total_area / 100) < area < (total_area / 3):
        return False

    if parent is None:
        # paper_not_visible
        return True
    else:
        parent_area = cv2.contourArea(parent)
        # paper_visible_condition
        if parent_area > (total_area / 3):
            return True
    return False


def order_contours(contours):
    # TODO: Clean up duplicate code with order_points()
    # ^ EHH ITS FINE
    assert 0 < len(contours) <= 4
    ordered_contours = [None for _ in range(4)]
    center_points = []
    for contour in contours:
        x_mean = np.mean(contour[:, 0, 0])
        y_mean = np.mean(contour[:, 0, 1])
        center_points.append([x_mean, y_mean])

    center_points = np.array(center_points)

    coordinates_sum = center_points.sum(1)
    coordinates_diff = np.diff(center_points, axis=1)
    ordered_contours[0] = contours[np.argmin(coordinates_sum)]  # topleft
    ordered_contours[1] = contours[np.argmax(coordinates_diff)]  # bottomleft
    ordered_contours[2] = contours[np.argmin(coordinates_diff)]  # topright
    ordered_contours[3] = contours[np.argmax(coordinates_sum)]  # bottomright

    return ordered_contours[: len(contours)]
    # return ordered_contours


def x_marks_the_spot(image, contours, correct_answers):
    cumulator = [[0, 0, 0, 0, 0] for _ in correct_answers]
    uncertains = [0 for _ in correct_answers]
    for threshold in range(16, 240, 4):
        warped_images = get_warped_images(
            image.shape[1], image.shape[0], contours, image, threshold1=threshold
        )
        given_answers = get_answers(warped_images)

        ### debug ###
        for k, img in enumerate(warped_images):
            cv2.imshow(f'img_{k}', img)
        print(f'{threshold=}')
        for k, ans in enumerate(given_answers, 1):
            if ans is None:
                print('0', end=' ')
            else:
                print('ABCD'[ans], end=' ')
            if k % 5 == 0: print('')
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        ### debug end ###

        for k, answer in enumerate(given_answers):
            if answer is not None:
                cumulator[k][answer] += 1
            else:
                uncertains[k] += 1
    given_answers = list()
    for k, (counts, uncertain) in enumerate(zip(cumulator, uncertains)):
        if max(counts) * 2 > sum(counts) and max(counts) * 20 > uncertain:
            given_answers.append(np.argmax(counts))
        else:
            given_answers.append(None)
    return warped_images, given_answers


def get_warped_images(width, height, contours, image, threshold1=150, threshold2=255):
    dst_matrix = np.array(
        [
            [0, 0],
            [width, 0],
            [0, height],
            [width, height],
        ],
        dtype="float32",
    )
    warped_images = []

    for k, contour in enumerate(contours):
        reordered_points = order_points(contour)

        matrix = cv2.getPerspectiveTransform(reordered_points, dst_matrix)

        warped_image = cv2.warpPerspective(image, matrix, (width, height))
        warped_image = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
        warped_image = cv2.threshold(warped_image, threshold1, threshold2, cv2.THRESH_BINARY_INV)[1]

        warped_image = cut_image_border(warped_image)
        warped_images.append(warped_image)
    return warped_images


def order_points(contour):
    points = contour.reshape((4, 2))
    reordered_points = np.zeros((4, 1, 2), dtype="float32")

    coordinates_sum = points.sum(1)
    reordered_points[0] = points[np.argmin(coordinates_sum)]  # [0, 0]
    reordered_points[3] = points[np.argmax(coordinates_sum)]  # [w, h]

    coordinates_diff = np.diff(points, axis=1)
    reordered_points[1] = points[np.argmin(coordinates_diff)]  # [w, 0]
    reordered_points[2] = points[np.argmax(coordinates_diff)]  # [0, h]
    return reordered_points


def cut_image_border(image):
    height, width = image.shape

    top_border = int(height // 100 * 3)
    image_height = height - top_border * 2
    image_height = int(5 * (int(image_height / 5)))
    top_border = int((height - image_height) / 2)

    side_border = int(width // 100 * 5)
    image_width = width - side_border * 2
    image_width = int(4 * (int(image_width / 4)))
    side_border = int((width - image_width) / 2)

    image = image[top_border : height - top_border, side_border : width - side_border]
    return image


def get_answers(warped_images):
    assessment_answers = []

    for warped_image in warped_images:
        boxes = get_boxes(warped_image)
        pixel_values = np.zeros((4, 1))
        for r, row in enumerate(boxes):
            for c, box in enumerate(row):
                cv2.countNonZero(box)
                box_size = box.shape[0] * box.shape[1]
                pixel_values[c] = cv2.countNonZero(box)
            sorted_values = sorted(pixel_values, reverse=True)
            if (
                sorted_values[0] - sorted_values[1]
                > box_size * 0.01 + sorted_values[1] - sorted_values[-1]
            ):
                assessment_answers.append(np.argmax(pixel_values))
            else:
                assessment_answers.append(None)

    return assessment_answers


def get_boxes(image, rows=5, cols=4):
    rows = np.vsplit(image, 5)
    boxes = []
    for r in rows:
        boxes.append(list())
        cols = np.hsplit(r, 4)
        for box in cols:
            boxes[-1].append(box)
    return boxes


def grade_test(warped_images, correct_answers, given_answers):
    points = 0
    no_answer = 0
    max_points = 0
    corrected_warped_images = []

    for image_index, warped_image in enumerate(warped_images):
        corrected_warped_image = np.zeros_like(warped_image)
        corrected_warped_image = cv2.cvtColor(corrected_warped_image, cv2.COLOR_GRAY2BGR)

        section_width = corrected_warped_image.shape[1] // 4
        section_height = corrected_warped_image.shape[0] // 5

        for x in range(5):
            max_points += 1
            given_answer = given_answers[image_index * 5 + x]
            correct_answer = correct_answers[image_index * 5 + x]
            if given_answer == correct_answer:
                points += 1
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)

            if given_answer is not None:
                center_x = (given_answer % 4) * section_width + section_width // 2
                center_y = (x) * section_height + section_height // 2
                cv2.circle(corrected_warped_image, (center_x, center_y), 100, color, cv2.FILLED)
            else:
                no_answer += 1

            correct_x = (correct_answer % 4) * section_width + section_width // 2
            correct_y = (x) * section_height + section_height // 2
            cv2.circle(corrected_warped_image, (correct_x, correct_y), 50, (0, 255, 0), cv2.FILLED)

        corrected_warped_images.append(corrected_warped_image)
    return f"{points}/{max_points} ({no_answer})", corrected_warped_images


def get_inverse_warped_images(width, height, contours, image, corrected_images):
    image_final = image.copy()
    dst_matrix = np.array(
        [
            [0, 0],
            [width, 0],
            [0, height],
            [width, height],
        ]
    ).astype("float32")
    for corrected_image, contour in zip(corrected_images, contours):
        reordered_points = order_points(contour)
        reordered_points = reordered_points.astype("float32")

        matrix = cv2.getPerspectiveTransform(dst_matrix, reordered_points)

        warped_image = cv2.warpPerspective(corrected_image, matrix, (width, height))
        cv2.addWeighted(warped_image, 1, image_final, 1, 0, image_final)

    return image_final




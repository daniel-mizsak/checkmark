"""
Code to generate the PDF document.
Underlying library: https://github.com/PyFPDF/fpdf2

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import base64
import os
import random
import sys
from dataclasses import dataclass

import qrcode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image

from checkmark.generator.question import Question


@dataclass
class PDFData:
    """Data necessary for the checkmark PDF generation."""

    student: str
    class_: str
    subject: str
    topic: str
    date: str
    questions: list[Question]
    pocket_id: str
    pocket_password: str


def create_pdf(pdf_data: PDFData) -> PDF:
    """Creates a PDF document from the given data."""
    pdf = PDF(pdf_data)
    pdf.add_page()
    pdf.add_questions()
    pdf.add_page()
    pdf.add_checkmark_boxes()
    return pdf


class PDF(FPDF):
    """PDF class for generating the checkmark PDF document."""

    def __init__(self, pdf_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alias_nb_pages()
        self.set_auto_page_break(auto=False)

        self.margin = 15
        self.set_margin(self.margin)

        font_path = f"{os.getcwd()}/data/app/FreeSans.ttf"
        self.add_font(fname=font_path, family="FreeSans")
        self.font = "FreeSans"
        self.title_font_size = 20
        self.question_font_size = 14
        self.option_font_size = 12
        self.footer_font_size = 8

        self.student = pdf_data.student
        self.class_ = pdf_data.class_
        self.subject = pdf_data.subject
        self.topic = pdf_data.topic
        self.date = pdf_data.date
        self.questions = pdf_data.questions
        self.pocket_id = pdf_data.pocket_id
        self.pocket_password = pdf_data.pocket_password

        self.question_number = 0
        self.last_page = False
        self.qr_pocket = self.create_pocket_qr_image()
        self.qr_solution = self.create_solution_qr_image()

    def header(self) -> None:
        self.set_font(self.font, "", self.title_font_size)
        self.ln(5)

        if self.page_no() == 1:
            assessment_data = [
                ["Név:", self.student],
                ["Osztály:", self.class_],
                ["Tantárgy:", self.subject],
            ]

            for row in assessment_data:
                for col_num, col in enumerate(row):
                    cell_width = self.w / 4 if col_num == 0 else self.w / 2
                    self.multi_cell(cell_width, 10, col, align="L", new_x="RIGHT", new_y="TOP")
                self.ln(10)
            self.ln(5)

            topic_text = f"{self.topic}"
            self.multi_cell(
                self.w * 0.7, 10, topic_text, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
            self.ln(10)

            qr_size = 50
            self.image(
                self.qr_pocket,
                self.w - (self.margin + qr_size) + 4,
                self.margin,
                qr_size,
            )

        if self.last_page:
            assessment_data = [
                ["Név:", self.student],
                ["Aláírás:", f"{'.' * 30}"],
            ]

            for row in assessment_data:
                for col_num, col in enumerate(row):
                    cell_width = self.w / 4 if col_num == 0 else self.w / 2
                    self.multi_cell(cell_width, 10, col, align="L", new_x="RIGHT", new_y="TOP")
                self.ln(20)
            self.ln(25)

            qr_size = 60
            self.image(
                self.qr_solution,
                self.w - (self.margin + qr_size) + 4,
                self.margin,
                qr_size,
            )

    def footer(self) -> None:
        self.set_y(-1 * self.margin + 5)
        self.set_font(self.font, "", self.footer_font_size)
        self.set_text_color(180, 180, 180)

        page_number_text = f"Oldal {self.page_no()}/{{nb}}"
        self.cell(0, 0, page_number_text, align="C")

        date_text = f"Dátum: {self.date.replace('-', '.')}."
        self.cell(0, 0, date_text, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def add_questions(self) -> None:
        """Displays the selected questions and options."""
        # TODO: Cell overflow is still not working due to changing text character width
        cell_width = (self.w - 2 * self.margin) / 4
        for question in self.questions:
            self.question_number += 1
            self.set_font(self.font, "", self.question_font_size)
            self.set_fill_color(200, 220, 255)
            chapter_title = f"{self.question_number}.: {question.body}"

            self.cell(0, 5, chapter_title, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(5)

            self.set_font(self.font, "", self.option_font_size)

            original_y = self.get_y()
            cell_overflow = 0
            for num, (letter, option) in enumerate(zip("ABCD", question.options)):
                self.set_x(self.margin + num * cell_width)
                self.multi_cell(cell_width, 5, f"{letter}) {option}", align="L")
                self.set_y(original_y)

                cell_overflow = max(
                    self.get_string_width(f"{letter}) {option}") // cell_width,
                    cell_overflow,
                )

            if self.h - self.get_y() < self.margin * 3 and question != self.questions[-1]:
                self.add_page()
            else:
                self.ln(10 + cell_overflow * 5)
        self.last_page = True

    def add_checkmark_boxes(self) -> None:
        """Displays the boxes at the last page, where the answers are selected."""
        # TODO: Give circles equal spaces from the borders
        number_of_blocks = ((len(self.questions) - 1) // 5) + 1

        total_width = self.w - 2 * self.margin
        column_width = total_width / 10

        circle_diameter = 10
        column_gap = column_width - circle_diameter

        rectangle_width = column_width * 4
        rectangle_height = 5 * circle_diameter + 4 * column_gap

        self.get_x()
        original_y = self.get_y()

        # TODO: Fix duplicate code
        for block in range(number_of_blocks):
            if block == 2:
                self.set_y(original_y)

            if block >= 2:
                self.set_x(self.get_x() + total_width / 2)

            # Options
            self.set_line_width(0.5)
            for s in " ABCD":
                self.cell(column_width, 0, s, align="C")
            self.cell(0, 5, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            if block >= 2:
                self.set_x(self.get_x() + total_width / 2)

            # Rectangles
            rectangle_x = self.get_x() + column_width
            rectangle_y = self.get_y()

            self.set_line_width(1.5)
            self.rect(
                rectangle_x,
                rectangle_y,
                rectangle_width,
                rectangle_height,
            )

            # Numbers
            self.set_line_width(0.5)
            self.set_y(self.get_y() + circle_diameter / 2)
            for question_number in range(1, 6):
                self.set_y(self.get_y() + circle_diameter / 2)

                if block >= 2:
                    self.set_x(self.get_x() + total_width / 2 + circle_diameter / 2)
                else:
                    self.set_x(self.get_x() + circle_diameter / 2)

                self.cell(circle_diameter, 0, str(block * 5 + question_number), align="C")
                self.set_x(self.get_x() + column_gap)
                self.set_y(self.get_y() - circle_diameter / 2)

                if block >= 2:
                    self.set_x(self.get_x() + total_width / 2)
                # Circles
                self.set_x(self.get_x() + column_gap / 2)
                for _ in range(4):
                    self.set_x(self.get_x() + column_width)
                    self.circle(self.get_x(), self.get_y(), r=circle_diameter)

                self.set_y(self.get_y() + 1.5 * circle_diameter)

            self.ln(15)

    def create_solution_qr_image(self) -> Image.Image:
        """Encodes the necessary information into a string and creates a QR code from it."""
        question_data = " ".join([str(question.index) for question in self.questions])
        correct_data = " ".join([str(question.correct) for question in self.questions])
        assessment_data = "; ".join([self.student, self.date, question_data, correct_data])

        random.seed(0)
        salt = random.getrandbits(128).to_bytes(16, sys.byteorder)
        kdf = PBKDF2HMAC(algorithm=SHA256(), length=32, salt=salt, iterations=1)
        key = base64.urlsafe_b64encode(kdf.derive(self.pocket_password.encode()))

        fernet = Fernet(key)
        token = fernet.encrypt(assessment_data.encode("utf-8"))
        qr_image = qrcode.make(token)
        qr_image = qr_image.convert("RGB")
        return qr_image

    def create_pocket_qr_image(self) -> Image.Image:
        """Creates a QR code pointing to the webpage where the assessment can be uploaded."""
        if not self.pocket_id:
            return Image.new("RGB", (1, 1), color="white")
        pocket_url = f"https://pythonvilag.hu/checkmark/pocket/{self.pocket_id}/"
        qr_image = qrcode.make(pocket_url)
        qr_image = qr_image.convert("RGB")
        return qr_image

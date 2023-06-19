import json
import os
import random
import re
import subprocess
import sys
import tkinter as tk
import webbrowser
from tkinter import messagebox

import requests
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import INFO, OUTLINE

from checkmark.generator.generate import generate_assessment


class GeneratorInterface(tk.Tk):
    def __init__(self) -> None:
        tk.Tk.__init__(self)
        window_width = 680
        window_height = 440

        # TODO: Add icon
        self.wm_title("Checkmark Generator")
        self.wm_geometry(f"{window_width}x{window_height}+200+200")
        self.wm_resizable(False, False)
        self.style = Style(theme="superhero")

        self.validator = InterfaceValidation()

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.topic_page = TopicPage(container, self)
        self.student_page = StudentPage(container, self)
        self.question_page = QuestionPage(container, self)
        self.data_page = DataPage(container, self)
        self.submit_page = SubmitPage(container, self)

        self.topic_page.grid(row=0, column=0, sticky="nsew")
        self.student_page.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.question_page.grid(row=1, column=0, sticky="nsew")
        self.data_page.grid(row=2, column=0, sticky="nsew")
        self.submit_page.grid(row=2, column=1, sticky="nsew")


class TopicPage(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: GeneratorInterface) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Class
        # TODO: Add styling to dropdown menu as well
        self.class_label = tk.Label(self, text="Osztály")
        self.available_classes = self.list_available_classes()
        self.class_stringvar = tk.StringVar()
        self.class_stringvar.set("Osztály kiválasztása")
        self.class_stringvar.trace("w", self.reset_subjects_and_update_student_listbox)
        self.class_menubutton = ttk.Menubutton(
            self,
            text=self.class_stringvar.get(),
            style="info.Outline.TMenubutton",
            width=15,
        )
        self.class_menu = tk.Menu(self.class_menubutton, tearoff=0)
        for class_name in self.available_classes:
            self.class_menu.add_radiobutton(
                label=class_name,
                value=class_name,
                variable=self.class_stringvar,
            )
        self.class_menubutton["menu"] = self.class_menu

        # Subject
        self.subject_label = tk.Label(self, text="Tantárgy")
        self.subject_stringvar = tk.StringVar()
        self.subject_stringvar.set("Tantárgy kiválasztása")
        self.subject_stringvar.trace("w", self.reset_topics)
        self.subject_menubutton = ttk.Menubutton(
            self,
            text=self.subject_stringvar.get(),
            style="info.Outline.TMenubutton",
            state="disabled",
            width=15,
        )
        self.subject_menu = tk.Menu(self.subject_menubutton, tearoff=0)

        # Topic
        self.topic_label = tk.Label(self, text="Témakör")
        self.topic_stringvar = tk.StringVar()
        self.topic_stringvar.set("Témakör kiválasztása")
        self.topic_stringvar.trace("w", self.change_topic_menubar_text)
        self.topic_menubutton = ttk.Menubutton(
            self,
            text=self.topic_stringvar.get(),
            style="info.Outline.TMenubutton",
            state="disabled",
            width=15,
        )
        self.topic_menu = tk.Menu(self.topic_menubutton, tearoff=0)

        # Grid
        self.class_label.grid(row=0, column=0, padx=10, pady=(15, 8), sticky="nw")
        self.class_menubutton.grid(row=0, column=1, padx=10, pady=(15, 8), sticky="ne")
        self.subject_label.grid(row=1, column=0, padx=10, pady=8, sticky="nw")
        self.subject_menubutton.grid(row=1, column=1, padx=10, pady=8, sticky="ne")
        self.topic_label.grid(row=2, column=0, padx=10, pady=8, sticky="nw")
        self.topic_menubutton.grid(row=2, column=1, padx=10, pady=8, sticky="ne")

    def reset_subjects_and_update_student_listbox(self, *args: str) -> None:
        self.class_menubutton.configure(text=self.class_stringvar.get())
        self.reset_subjects()
        self.controller.student_page.update_student_listbox()

    def reset_subjects(self) -> None:
        class_number = self.class_stringvar.get().split("-")[0]
        self.available_subjects = self.list_available_subjects(class_number)

        self.subject_stringvar.set("Tantárgy kiválasztása")
        self.subject_menubutton.configure(state="normal")
        self.subject_menu.delete(0, "end")

        for subject in self.available_subjects:
            subject = subject.split("-")[0]
            self.subject_menu.add_radiobutton(
                label=subject,
                value=subject,
                variable=self.subject_stringvar,
            )
        self.subject_menubutton["menu"] = self.subject_menu
        self.reset_topics()

    def reset_topics(self, *args: str) -> None:
        class_number = self.class_stringvar.get()
        subject_name = self.subject_stringvar.get()

        self.subject_menubutton.configure(text=subject_name)
        self.topic_stringvar.set("Témakör kiválasztása")

        # TODO: There should be a better way to do this
        if subject_name == "Tantárgy kiválasztása":
            self.topic_menubutton.configure(state="disabled")
            self.topic_menu.delete(0, "end")
        else:
            self.topic_menubutton.configure(state="normal")
            self.topic_menu.delete(0, "end")

            self.available_topics = self.list_available_topics(
                class_number.split("-")[0],
                subject_name.split("-")[0],
            )

            for available_topic in self.available_topics:
                topic = available_topic.split(".")[0].replace("_", " ").split(" ")
                topic[0] += "."
                topic_value = " ".join(topic)
                self.topic_menu.add_radiobutton(
                    label=topic_value,
                    value=topic_value,
                    variable=self.topic_stringvar,
                )
            self.topic_menubutton["menu"] = self.topic_menu

    def change_topic_menubar_text(self, *args: str) -> None:
        self.topic_menubutton.configure(text=self.topic_stringvar.get())

    @staticmethod
    def list_available_classes() -> list[str]:
        available_classes = []
        for class_name in os.listdir("data/classes"):
            if class_name.endswith(".csv"):
                index = class_name.rindex(".")
                available_classes.append(class_name[:index])

        def compare_class_numbers(class_name: str) -> tuple[int, str]:
            number, letter = class_name.split("-")
            return int(number), letter

        available_classes = sorted(set(available_classes), key=compare_class_numbers)
        return available_classes

    @staticmethod
    def list_available_subjects(class_number: str) -> list[str]:
        available_subjects = []
        for subject_name in os.listdir("data/assessments"):
            subject_name_is_directory = os.path.isdir(f"data/assessments/{subject_name}")
            subject_name_matches_class = subject_name.split("-")[-1] == class_number
            if subject_name_is_directory and subject_name_matches_class:
                available_subjects.append(subject_name)
        available_subjects = sorted(list(set(available_subjects)))
        return available_subjects

    @staticmethod
    def list_available_topics(class_number: str, subject_name: str) -> list[str]:
        available_topics = []
        for topic_name in os.listdir(f"data/assessments/{subject_name}-{class_number}"):
            if topic_name.endswith(".xlsx"):
                available_topics.append(topic_name)

        def compare_topic_numbers(topic_name: str) -> tuple[int, str]:
            number, letter = topic_name.split("_", maxsplit=1)
            return int(number), letter

        available_topics = sorted(list(set(available_topics)), key=compare_topic_numbers)
        return available_topics


class StudentPage(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: GeneratorInterface) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=0)
        self.grid_rowconfigure(3, weight=1)

        # Student number
        self.student_number_label = ttk.Label(self, text="Sorsolt diák szám")
        self.student_number_spinbox = ttk.Spinbox(self, from_=1, to=40, width=5)
        self.student_number_spinbox.set(5)

        # Select random students
        self.select_random_students_button = ttk.Button(
            self,
            text="Sorsolj",
            command=self.select_random_students,
            bootstyle=(INFO, OUTLINE),
            width=10,
        )

        # Select students
        self.select_students_button = ttk.Button(
            self,
            text="Összes",
            command=self.select_students,
            bootstyle=(INFO, OUTLINE),
            width=10,
        )

        # Students
        # TODO: Change the color of the selected items for better visibility
        # TODO: When double clicking other field it deselects the selected items
        self.available_students: list[str] = []
        self.student_listbox = tk.Listbox(self, selectmode="multiple")
        self.student_listbox.event_generate("<<ListboxSelect>>")
        self.student_listbox.bind("<<ListboxSelect>>", self.update_select_button)

        self.student_listbox_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.student_listbox_scrollbar.config(command=self.student_listbox.yview)
        self.student_listbox.config(yscrollcommand=self.student_listbox_scrollbar.set)

        # Grid
        self.student_number_label.grid(
            row=0, column=0, columnspan=2, padx=10, pady=(15, 8), sticky="nw"
        )
        self.student_number_spinbox.grid(
            row=0, column=2, columnspan=2, padx=10, pady=(15, 8), sticky="ne"
        )
        self.select_random_students_button.grid(row=1, column=0, padx=10, pady=8, sticky="nw")
        self.select_students_button.grid(
            row=1, column=1, columnspan=3, padx=10, pady=8, sticky="ne"
        )
        self.student_listbox.grid(
            row=3, column=0, columnspan=3, padx=(10, 0), pady=8, sticky="nsew"
        )
        self.student_listbox_scrollbar.grid(row=3, column=3, padx=(0, 10), pady=8, sticky="ns")

    def update_student_listbox(self) -> None:
        class_selected = self.controller.topic_page.class_stringvar.get()
        with open(
            file=f"data/classes/{class_selected}.csv",
            mode="r",
            encoding="utf-8",
        ) as f:
            self.available_students = f.readline().strip().split(", ")

        self.student_listbox.delete(0, tk.END)
        for available_student in self.available_students:
            self.student_listbox.insert(tk.END, available_student)

    def select_random_students(self) -> None:
        student_number = self.student_number_spinbox.get()
        if self.controller.validator.validate_student_number(
            student_number, self.available_students
        ):
            student_number = int(student_number)
            students_selected = random.sample(self.available_students, k=student_number)
            self.student_listbox.selection_clear(0, tk.END)
            for student in students_selected:
                self.student_listbox.selection_set(self.available_students.index(student))
            self.update_select_button()

    def select_students(self) -> None:
        if self.controller.validator.validate_available_students(self.available_students):
            if len(self.student_listbox.curselection()) != len(self.available_students):
                self.student_listbox.selection_set(0, tk.END)
            else:
                self.student_listbox.selection_clear(0, tk.END)
            self.update_select_button()

    def update_select_button(self, *args) -> None:  # type: ignore
        if len(self.student_listbox.curselection()) != len(self.available_students):
            self.select_students_button.configure(text="Összes")
        else:
            self.select_students_button.configure(text="Egyik sem")


class QuestionPage(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: GeneratorInterface) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Question number
        self.question_number_label = tk.Label(self, text="Kérdések száma")
        self.question_number_spinbox = ttk.Spinbox(
            self, from_=1, to=20, textvariable=tk.IntVar(), width=5
        )
        self.question_number_spinbox.set(20)

        # Random question order
        self.random_question_order_label = tk.Label(self, text="Véletlenszerű kérdés sorrend")
        self.random_question_order_booleanvar = tk.BooleanVar(value=True)
        self.random_question_order_checkbutton = tk.Checkbutton(
            self,
            variable=self.random_question_order_booleanvar,
            onvalue=True,
            offvalue=False,
        )

        # Random option order
        self.random_option_order_label = tk.Label(self, text="Véletlenszerű opció sorrend")
        self.random_option_order_booleanvar = tk.BooleanVar(value=True)
        self.random_option_order_checkbutton = tk.Checkbutton(
            self,
            variable=self.random_option_order_booleanvar,
            onvalue=True,
            offvalue=False,
        )

        # Grid
        self.question_number_label.grid(row=0, column=0, padx=10, pady=8, sticky="nw")
        self.question_number_spinbox.grid(row=0, column=1, padx=10, pady=8, sticky="ne")
        self.random_question_order_label.grid(row=1, column=0, padx=10, pady=8, sticky="nw")
        self.random_question_order_checkbutton.grid(row=1, column=1, padx=10, pady=8, sticky="ne")
        self.random_option_order_label.grid(row=2, column=0, padx=10, pady=8, sticky="nw")
        self.random_option_order_checkbutton.grid(row=2, column=1, padx=10, pady=8, sticky="ne")


class DataPage(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: GeneratorInterface) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # E-mail
        self.email_label = tk.Label(self, text="E-mail cím")
        self.email_entry = ttk.Entry(self, justify="left", width=20)
        self.email_entry.insert(0, self.load_email())

        # Online evaluator
        self.online_evaluator_label = tk.Label(self, text="Internetes javító létrehozása")
        self.online_evaluator_booleanvar = tk.BooleanVar(value=False)
        self.online_evaluator_booleanvar.trace("w", self.online_evaluator_connection)
        self.online_evaluator_checkbutton = tk.Checkbutton(
            self,
            variable=self.online_evaluator_booleanvar,
            onvalue=True,
            offvalue=False,
        )

        # Date
        self.date_label = tk.Label(self, text="Dátum")
        self.date_entry = ttk.DateEntry(self, width=10, dateformat="%Y-%m-%d", firstweekday=0)

        # Grid
        self.email_label.grid(row=0, column=0, padx=10, pady=8, sticky="nw")
        self.email_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ne")
        self.online_evaluator_label.grid(row=1, column=0, padx=10, pady=8, sticky="nw")
        self.online_evaluator_checkbutton.grid(row=1, column=1, padx=10, pady=8, sticky="ne")
        self.date_label.grid(row=2, column=0, padx=10, pady=(8, 15), sticky="nw")
        self.date_entry.grid(row=2, column=1, padx=10, pady=(8, 15), sticky="ne")

    def deselect_checkbutton(self) -> None:
        self.online_evaluator_checkbutton.config(variable=tk.BooleanVar(value=False))
        self.online_evaluator_booleanvar.set(False)
        self.online_evaluator_checkbutton.config(variable=self.online_evaluator_booleanvar)

    def online_evaluator_connection(self, *args: str) -> None:
        if self.online_evaluator_booleanvar.get():
            if not self.controller.validator.validate_online_evaluator_connection():
                self.deselect_checkbutton()

    @staticmethod
    def load_email() -> str:
        try:
            with open("data/app_data/data.json", "r", encoding="utf-8") as f:
                email_address = json.loads(f.read())["email"]
        except FileNotFoundError:
            email_address = ""
        return email_address

    @staticmethod
    def save_email(email: str) -> None:
        with open("data/app_data/data.json", "r+", encoding="utf-8") as f:
            data = json.loads(f.read())
            data["email"] = email
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4, ensure_ascii=False)


class SubmitPage(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: GeneratorInterface) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Submit
        self.controller.style.configure("my.info.Outline.TButton", font=(None, 18))
        self.submit_button = ttk.Button(
            self,
            text="Küldés",
            command=self.submit,
        )
        self.submit_button.config(style="my.info.Outline.TButton")

        # Feedback
        self.feedback_label = tk.Label(self, text="Visszajelzés küldése")
        self.feedback_label.bind("<Button-1>", lambda e: self.send_feedback())

        # Grid
        self.submit_button.grid(
            row=0, column=0, ipadx=20, ipady=12, padx=10, pady=(15, 8), sticky="n"
        )
        self.feedback_label.grid(row=1, column=0, padx=10, pady=(8, 15), sticky="s")

    def submit(self) -> None:
        student_indices = self.controller.student_page.student_listbox.curselection()
        checkmark_fields: dict[str, str | list[str] | bool | int] = {
            "osztaly": str(self.controller.topic_page.class_stringvar.get()),
            "tantargy": str(self.controller.topic_page.subject_stringvar.get()),
            "temakor": str(self.controller.topic_page.topic_stringvar.get()),
            "tanulok": list(
                str(self.controller.student_page.student_listbox.get(index))
                for index in student_indices
            ),
            "email": str(self.controller.data_page.email_entry.get()),
            "online_kiertekeles": bool(self.controller.data_page.online_evaluator_booleanvar.get()),
            "datum": str(self.controller.data_page.date_entry.entry.get()),
            "kerdesek_szama": int(
                self.controller.question_page.question_number_spinbox.get()
            ),  # TODO: Validate before converting
            "veletlenszeru_kerdesek": bool(
                self.controller.question_page.random_question_order_booleanvar.get()
            ),
            "veletlenszeru_valaszok": bool(
                self.controller.question_page.random_option_order_booleanvar.get()
            ),
        }

        if not self.controller.validator.validate_checkmark_fields(checkmark_fields):
            return

        self.controller.data_page.save_email(str(checkmark_fields["email"]))

        try:
            generate_assessment(**checkmark_fields)  # type: ignore
            messagebox.showinfo("Siker!", "A dolgozatok elkészültek!")
        except Exception as e:
            messagebox.showerror("Hiba!", f"Hiba történt a dolgozatok elkészítése során:\n{e}")

    @staticmethod
    def send_feedback() -> None:
        recipient = "info@pythonvilag.hu"
        subject = "Checkmark visszajelzés"
        webbrowser.open("mailto:?to=" + recipient + "&subject=" + subject, new=1)

    @staticmethod
    def generate_subprocess_call(checkmark_fields: dict[str, str | list[str] | bool | int]) -> None:
        """
        This function can be used if we want to call the generate function from the command line,
        instead of importing it.
        """
        # TODO: Fix problem regarding PYTHONPATH and subprocess
        subprocess_call = [
            sys.executable,
            "-m checkmark.generator.generate",
            f"--osztaly={checkmark_fields['osztaly']}",
            f"--tantargy={checkmark_fields['tantargy']}",
            f"--temakor={checkmark_fields['temakor']}",
            *(f"--tanulok={student}" for student in checkmark_fields["tanulok"]),  # type: ignore
            f"--email={checkmark_fields['email']}",
            f"--datum={checkmark_fields['datum']}",
            f"--kerdesek_szama={checkmark_fields['kerdesek_szama']}",
        ]

        if checkmark_fields["online_kiertekeles"]:
            subprocess_call.append("--online_kiertekeles=1")
        if checkmark_fields["veletlenszeru_kerdesek"]:
            subprocess_call.append("--veletlenszeru_kerdesek=1")
        if checkmark_fields["veletlenszeru_valaszok"]:
            subprocess_call.append("--veletlenszeru_valaszok=1")

        try:
            checkmark_response = subprocess.check_output(subprocess_call)
            messagebox.showinfo("Siker!", "A dolgozatok elkészültek!")
        except subprocess.CalledProcessError:
            # TODO: Give more information about the error
            messagebox.showerror("Hiba!", "Valami hiba történt a dolgozatok elkészítése során.")


class InterfaceValidation:
    def validate_checkmark_fields(
        self, checkmark_fields: dict[str, str | list[str] | bool | int]
    ) -> bool:
        missing_field_name = None
        for field_name, field in checkmark_fields.items():
            if field_name == "osztaly" and "kiválasztása" in str(field):
                missing_field_name = "osztály"
                break
            elif field_name == "tantargy" and "kiválasztása" in str(field):
                missing_field_name = "tantárgy"
                break
            elif field_name == "temakor" and "kiválasztása" in str(field):
                missing_field_name = "témakör"
                break
            elif not field and field_name == "tanulok":
                missing_field_name = "tanulók"
                break
            elif field_name == "email":
                if not field:
                    missing_field_name = "email"
                    break
                elif not self._validate_email(str(field)):
                    messagebox.showerror("Hibás adat", "Az e-mail cím formátuma nem megfelelő!")
                    return False
            elif field_name == "kerdesek_szama" and not self._validate_question_number(str(field)):
                return False

        if missing_field_name:
            messagebox.showerror("Hiányzó adat", f"Kérlek add meg a(z) {missing_field_name} mezőt!")
            return False
        return True

    @staticmethod
    def _validate_email(email: str) -> bool:
        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not re.match(email_regex, email):
            return False
        return True

    @staticmethod
    def _validate_question_number(question_number: str) -> bool:
        try:
            int(question_number)
        except ValueError:
            messagebox.showerror("Hibás adat", "A kérdések száma csak egész szám lehet!")
            return False
        if not (1 <= int(question_number) <= 20):
            messagebox.showerror("Hibás adat", "A kérdések száma csak 1 és 20 közötti érték lehet!")
            return False
        return True

    def validate_student_number(self, student_number: str, available_students: list[str]) -> bool:
        if not self.validate_available_students(available_students):
            return False
        try:
            student_number_int = int(student_number)
        except ValueError:
            messagebox.showerror("Hibás adat", "A sorsolt diák szám csak egész szám lehet!")
            return False
        if not 1 <= student_number_int:
            messagebox.showerror(
                "Hibás adat",
                "A sorsolt diák szám csak 1 és az összes diák száma közötti érték lehet!",
            )
            return False
        return True

    @staticmethod
    def validate_available_students(available_students: list[str]) -> bool:
        if not available_students:
            messagebox.showerror("Hiányzó adat", "Kérlek először add meg az osztály mezőt!")
            return False
        return True

    def validate_online_evaluator_connection(self) -> bool:
        if not self._validate_connection("http://google.com"):
            messagebox.showerror(
                "Hálózati hiba",
                "Nem sikerült csatlakozni az internethez.",
            )
            return False

        if not self._validate_connection("http://127.0.0.1:5000/checkmark/create-pocket/"):
            # TODO: Update URL to final address
            messagebox.showerror(
                "Hálózati hiba",
                "Nem sikerült csatlakozni a szerverhez.",
            )
            return False
        return True

    @staticmethod
    def _validate_connection(url: str) -> bool:
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return False
        if response.status_code != 200:
            return False
        return True

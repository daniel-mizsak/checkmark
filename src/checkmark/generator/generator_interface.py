"""
Graphical User Interface that aggregates necessary information for assessment generation.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import json
import os
import platform
import random
import subprocess
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox

import requests
import ttkbootstrap as ttk
from ttkbootstrap import Style

from checkmark.generator.generate import CheckmarkFields, generate_assessment


class GeneratorInterface(tk.Tk):
    """Graphical User Interface for assessment generation."""

    def __init__(self: GeneratorInterface, interface_language: str = "HUN") -> None:
        """Constructor of the GeneratorInterface class.

        Args:
            self (GeneratorInterface): The GeneratorInterface object.
            interface_language (str, optional): The language of the interface. Defaults to "HUN".
        """
        # TODO: Support multiple languages
        tk.Tk.__init__(self)
        with Path("data/app/interface_language.json").open("r", encoding="utf-8") as file_handle:
            self.interface_language = json.load(file_handle)["generator"][interface_language]

        # self.iconphoto(True, tk.PhotoImage(file="data/app/icon.png"))  # noqa: ERA001
        self.wm_title(self.interface_language["title"])
        window_width = 680
        window_height = 440
        top_left_x = (self.winfo_screenwidth() - window_width) // 2
        top_left_y = (self.winfo_screenheight() - window_height) // 2
        self.wm_geometry(f"{window_width}x{window_height}+{top_left_x}+{top_left_y}")
        self.wm_resizable(width=False, height=False)
        self.style = Style(theme="superhero")

        self.validator = InterfaceValidation(self)

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
    """Top-Left part of the GUI. Responsible for selecting the class, subject and topic."""

    def __init__(self: TopicPage, parent: tk.Frame, controller: GeneratorInterface) -> None:
        """Constructor of the TopicPage class.

        Args:
            self (TopicPage): The TopicPage object.
            parent (tk.Frame): The parent of the TopicPage object.
            controller (GeneratorInterface): The GeneratorInterface object.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.topic_page_language = controller.interface_language["topic_page"]

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Class
        # TODO: Add styling to dropdown menu as well
        self.class_label = tk.Label(self, text=self.topic_page_language["class_label"])
        self.available_classes = self._list_available_classes()
        self.class_stringvar = tk.StringVar()
        self.class_stringvar.set(self.topic_page_language["class_stringvar"])
        self.class_stringvar.trace(
            "w",
            self._reset_subjects_and_update_student_listbox,  # type: ignore [no-untyped-call]
        )
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
        self.subject_label = tk.Label(self, text=self.topic_page_language["subject_label"])
        self.available_subjects: list[str] = []
        self.subject_stringvar = tk.StringVar()
        self.subject_stringvar.set(self.topic_page_language["subject_stringvar"])
        self.subject_stringvar.trace("w", self._reset_topics)  # type: ignore [no-untyped-call]
        self.subject_menubutton = ttk.Menubutton(
            self,
            text=self.subject_stringvar.get(),
            style="info.Outline.TMenubutton",
            state="disabled",
            width=15,
        )
        self.subject_menu = tk.Menu(self.subject_menubutton, tearoff=0)

        # Topic
        self.topic_label = tk.Label(self, text=self.topic_page_language["topic_label"])
        self.available_topics: list[str] = []
        self.topic_stringvar = tk.StringVar()
        self.topic_stringvar.set(self.topic_page_language["topic_stringvar"])
        self.topic_stringvar.trace("w", self._change_topic_menubar_text)  # type: ignore [no-untyped-call]
        self.topic_menubutton = ttk.Menubutton(
            self,
            text=self.topic_stringvar.get(),
            style="info.Outline.TMenubutton",
            state="disabled",
            width=15,
        )
        self.topic_menu = tk.Menu(self.topic_menubutton, tearoff=0)

        # Grid
        self.class_label.grid(row=0, column=0, padx=10, pady=(18, 8), sticky="nw")
        self.class_menubutton.grid(row=0, column=1, padx=10, pady=(18, 8), sticky="ne")
        self.subject_label.grid(row=1, column=0, padx=10, pady=8, sticky="nw")
        self.subject_menubutton.grid(row=1, column=1, padx=10, pady=8, sticky="ne")
        self.topic_label.grid(row=2, column=0, padx=10, pady=(8, 18), sticky="nw")
        self.topic_menubutton.grid(row=2, column=1, padx=10, pady=(8, 18), sticky="ne")

    def _reset_subjects_and_update_student_listbox(  # type: ignore [no-untyped-def]
        self: TopicPage,
        *args,  # noqa: ANN002, ARG002
    ) -> None:
        """Function to reset the subject and update the student list when the class is changed."""
        self.class_menubutton.configure(text=self.class_stringvar.get())
        self._reset_subjects()
        self.controller.student_page.update_student_listbox()

    def _reset_subjects(self: TopicPage) -> None:
        """Reloads the possible subjects based on the selected class."""
        class_number = self.class_stringvar.get().split("-")[0]
        self.available_subjects = self._list_available_subjects(class_number)

        self.subject_stringvar.set(self.topic_page_language["subject_stringvar"])
        self.subject_menubutton.configure(state="normal")
        self.subject_menu.delete(0, "end")

        for subject in self.available_subjects:
            subject_text = subject.split("-")[0]
            self.subject_menu.add_radiobutton(
                label=subject_text,
                value=subject_text,
                variable=self.subject_stringvar,
            )
        self.subject_menubutton["menu"] = self.subject_menu
        self._reset_topics()

    def _reset_topics(self: TopicPage, *args) -> None:  # type: ignore [no-untyped-def]  # noqa: ANN002, ARG002
        """Reloads the possible topics based on the selected class and subject."""
        class_number = self.class_stringvar.get()
        subject_name = self.subject_stringvar.get()

        self.subject_menubutton.configure(text=subject_name)
        self.topic_stringvar.set(self.topic_page_language["topic_stringvar"])

        # TODO: There might be a better way to do this
        if subject_name == self.topic_page_language["subject_stringvar"]:
            self.topic_menubutton.configure(state="disabled")
            self.topic_menu.delete(0, "end")
        else:
            self.topic_menubutton.configure(state="normal")
            self.topic_menu.delete(0, "end")

            self.available_topics = self._list_available_topics(
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

    def _change_topic_menubar_text(  # type: ignore [no-untyped-def]
        self: TopicPage,
        *args,  # noqa: ANN002, ARG002
    ) -> None:
        """Change the text of the topic menubar when a topic is selected."""
        self.topic_menubutton.configure(text=self.topic_stringvar.get())

    @staticmethod
    def _list_available_classes() -> list[str]:
        """
        Checks the "data/classes" directory for .csv files for available classes.

        Returns:
            list[str]: List of the class numbers in ascending order.
        """
        available_classes: list[str] = []
        for class_name in os.listdir("data/classes"):
            if class_name.endswith(".csv"):
                index = class_name.rindex(".")
                available_classes.append(class_name[:index])

        def compare_class_numbers(class_name: str) -> tuple[int, str]:
            number, letter = class_name.split("-")
            return int(number), letter

        return sorted(set(available_classes), key=compare_class_numbers)

    @staticmethod
    def _list_available_subjects(class_number: str) -> list[str]:
        """
        Checks the "data/assessments" directory for available subjects that corresponds to the selected class.

        Args:
            class_number (str): The number of the selected class.

        Returns:
            list[str]: List of the available subjects in ascending order.
        """
        available_subjects = []
        for subject_name in os.listdir("data/assessments"):
            subject_name_is_directory = Path(f"data/assessments/{subject_name}").is_dir()
            subject_name_matches_class = subject_name.split("-")[-1] == class_number
            if subject_name_is_directory and subject_name_matches_class:
                available_subjects.append(subject_name)
        return sorted(set(available_subjects))

    @staticmethod
    def _list_available_topics(class_number: str, subject_name: str) -> list[str]:
        """
        Checks the "data/assessments" directory for available topics that corresponds to the selected class and subject.

        Args:
            class_number (str): Number of the selected class.
            subject_name (str): Name of the selected subject.

        Returns:
            list[str]: List of the available topics in ascending order.
        """
        topic_names = os.listdir(f"data/assessments/{subject_name}-{class_number}")
        available_topics = [t for t in topic_names if t.endswith(".xlsx")]

        def _compare_topic_numbers(topic_name: str) -> tuple[int, str]:
            number, letter = topic_name.split("_", maxsplit=1)
            return int(number), letter

        return sorted(set(available_topics), key=_compare_topic_numbers)


class StudentPage(tk.Frame):
    """Top-Right part of the GUI. Responsible for selecting the students."""

    def __init__(self: StudentPage, parent: tk.Frame, controller: GeneratorInterface) -> None:
        """Constructor of the StudentPage class.

        Args:
            self (StudentPage): The StudentPage object.
            parent (tk.Frame): The parent of the StudentPage object.
            controller (GeneratorInterface): The GeneratorInterface object.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.student_page_language = self.controller.interface_language["student_page"]

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=0)
        self.grid_rowconfigure(3, weight=1)

        # Student number
        self.student_number_label = ttk.Label(self, text=self.student_page_language["student_number_label"])
        self.student_number_spinbox = ttk.Spinbox(self, from_=1, to=40, width=5)
        self.student_number_spinbox.set(5)

        # Select random students
        self.select_random_students_button = ttk.Button(
            self,
            text=self.student_page_language["select_random_students_button"],
            command=self._select_random_students,
            bootstyle=("info", "outline"),
            width=10,
        )

        # Select students
        self.select_students_button = ttk.Button(
            self,
            text=self.student_page_language["select_students_button_all"],
            command=self._select_students,
            bootstyle=("info", "outline"),
            width=10,
        )

        # Students
        # TODO: Change the color of the selected items for better visibility
        # TODO: When double clicking other field it deselects the previously selected items
        self.available_students: list[str] = []
        self.student_listbox = tk.Listbox(self, selectmode="multiple")
        self.student_listbox.event_generate("<<ListboxSelect>>")
        self.student_listbox.bind("<<ListboxSelect>>", self._update_select_button)

        self.student_listbox_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.student_listbox_scrollbar.config(command=self.student_listbox.yview)
        self.student_listbox.config(yscrollcommand=self.student_listbox_scrollbar.set)

        # Grid
        self.student_number_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(18, 8), sticky="nw")
        self.student_number_spinbox.grid(row=0, column=2, columnspan=2, padx=10, pady=(18, 8), sticky="ne")
        self.select_random_students_button.grid(row=1, column=0, padx=10, pady=8, sticky="nw")
        self.select_students_button.grid(row=1, column=1, columnspan=3, padx=10, pady=8, sticky="ne")
        self.student_listbox.grid(row=3, column=0, columnspan=3, padx=(10, 0), pady=8, sticky="nsew")
        self.student_listbox_scrollbar.grid(row=3, column=3, padx=(0, 10), pady=8, sticky="ns")

    def update_student_listbox(self: StudentPage) -> None:
        """Updates the student listbox with the available students from the selected class."""
        class_selected = self.controller.topic_page.class_stringvar.get()
        class_content_path = Path(f"data/classes/{class_selected}.csv")
        with class_content_path.open(mode="r", encoding="utf-8") as file_handle:
            self.available_students = file_handle.readline().strip().split(", ")

        self.student_listbox.delete(0, tk.END)
        for available_student in self.available_students:
            self.student_listbox.insert(tk.END, available_student)

    def _select_random_students(self: StudentPage) -> None:
        """Selects the number of students randomly from the available students."""
        student_number = self.student_number_spinbox.get()
        if self.controller.validator.validate_student_number(student_number, self.available_students):
            student_number = int(student_number)
            students_selected = random.sample(self.available_students, k=student_number)
            self.student_listbox.selection_clear(0, tk.END)
            for student in students_selected:
                self.student_listbox.selection_set(self.available_students.index(student))
            self._update_select_button()

    def _select_students(self: StudentPage) -> None:
        """Selects all of the student if not all selected, otherwise deselects them."""
        if self.controller.validator.validate_available_students(self.available_students):
            if len(self.student_listbox.curselection()) != len(self.available_students):  # type: ignore [no-untyped-call]  # noqa: E501
                self.student_listbox.selection_set(0, tk.END)
            else:
                self.student_listbox.selection_clear(0, tk.END)
            self._update_select_button()

    def _update_select_button(self: StudentPage, *args) -> None:  # type: ignore [no-untyped-def]  # noqa: ANN002, ARG002, E501
        """Updates the text of the select students button."""
        if len(self.student_listbox.curselection()) != len(self.available_students):  # type: ignore [no-untyped-call]
            self.select_students_button.configure(text=self.student_page_language["select_students_button_all"])
        else:
            self.select_students_button.configure(text=self.student_page_language["select_students_button_none"])


class QuestionPage(tk.Frame):
    """Middle-Left part of the GUI. Responsible for the question specific settings."""

    def __init__(self: QuestionPage, parent: tk.Frame, controller: GeneratorInterface) -> None:
        """Constructor of the QuestionPage class.

        Args:
            self (QuestionPage): The QuestionPage object.
            parent (tk.Frame): The parent of the QuestionPage object.
            controller (GeneratorInterface): The GeneratorInterface object.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.question_page_language = self.controller.interface_language["question_page"]

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Question number
        self.question_number_label = tk.Label(self, text=self.question_page_language["question_number_label"])
        self.question_number_spinbox = ttk.Spinbox(self, from_=1, to=20, textvariable=tk.IntVar(), width=5)
        self.question_number_spinbox.set(20)

        # Random question order
        self.random_question_order_label = tk.Label(
            self,
            text=self.question_page_language["random_question_order_label"],
        )
        self.random_question_order_booleanvar = tk.BooleanVar(value=True)
        self.random_question_order_checkbutton = tk.Checkbutton(
            self,
            variable=self.random_question_order_booleanvar,
            onvalue=True,
            offvalue=False,
        )

        # Random option order
        self.random_option_order_label = tk.Label(self, text=self.question_page_language["random_option_order_label"])
        self.random_option_order_booleanvar = tk.BooleanVar(value=True)
        self.random_option_order_checkbutton = tk.Checkbutton(
            self,
            variable=self.random_option_order_booleanvar,
            onvalue=True,
            offvalue=False,
        )

        # Grid
        self.question_number_label.grid(row=0, column=0, padx=10, pady=(18, 8), sticky="nw")
        self.question_number_spinbox.grid(row=0, column=1, padx=10, pady=(18, 8), sticky="ne")
        self.random_question_order_label.grid(row=1, column=0, padx=10, pady=8, sticky="nw")
        self.random_question_order_checkbutton.grid(row=1, column=1, padx=10, pady=8, sticky="ne")
        self.random_option_order_label.grid(row=2, column=0, padx=10, pady=(8, 18), sticky="nw")
        self.random_option_order_checkbutton.grid(row=2, column=1, padx=10, pady=(8, 18), sticky="ne")


class DataPage(tk.Frame):
    """Bottom-Left part of the GUI. Responsible for the general data settings."""

    def __init__(self: DataPage, parent: tk.Frame, controller: GeneratorInterface) -> None:
        """Constructor of the DataPage class.

        Args:
            self (DataPage): The DataPage object.
            parent (tk.Frame): The parent of the DataPage object.
            controller (GeneratorInterface): The GeneratorInterface object.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.data_page_language = self.controller.interface_language["data_page"]

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Online evaluator
        self.online_evaluator_label = tk.Label(self, text=self.data_page_language["online_evaluator_label"])
        self.online_evaluator_booleanvar = tk.BooleanVar(value=False)
        self.online_evaluator_booleanvar.trace("w", self.online_evaluator_connection)  # type: ignore [no-untyped-call]
        self.online_evaluator_checkbutton = tk.Checkbutton(
            self,
            variable=self.online_evaluator_booleanvar,
            onvalue=True,
            offvalue=False,
        )

        # Date
        self.date_label = tk.Label(self, text=self.data_page_language["date_label"])
        self.date_entry = ttk.DateEntry(self, width=10, dateformat="%Y-%m-%d", firstweekday=0)

        # Grid
        self.online_evaluator_label.grid(row=0, column=0, padx=10, pady=(30, 8), sticky="nw")
        self.online_evaluator_checkbutton.grid(row=0, column=1, padx=10, pady=(30, 8), sticky="ne")
        self.date_label.grid(row=1, column=0, padx=10, pady=(8, 18), sticky="nw")
        self.date_entry.grid(row=1, column=1, padx=10, pady=(8, 18), sticky="ne")

    def deselect_checkbutton(self: DataPage) -> None:
        """Deselects the online evaluator checkbutton if there is no connection."""
        self.online_evaluator_checkbutton.config(variable=tk.BooleanVar(value=False))
        self.online_evaluator_booleanvar.set(value=False)
        self.online_evaluator_checkbutton.config(variable=self.online_evaluator_booleanvar)

    def online_evaluator_connection(self: DataPage, *args) -> None:  # type: ignore [no-untyped-def]  # noqa: ANN002, ARG002, E501
        """Checks for online evaluator connection if the checkbutton is selected."""
        if (
            self.online_evaluator_booleanvar.get()
            and not self.controller.validator.validate_online_evaluator_connection()
        ):
            self.deselect_checkbutton()


class SubmitPage(tk.Frame):
    """Bottom-Right part of the GUI. Responsible for submitting the test and sending feedback."""

    def __init__(self: SubmitPage, parent: tk.Frame, controller: GeneratorInterface) -> None:
        """Constructor of the SubmitPage class.

        Args:
            self (SubmitPage): The SubmitPage object.
            parent (tk.Frame): The parent of the SubmitPage object.
            controller (GeneratorInterface): The GeneratorInterface object.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.submit_page_language = self.controller.interface_language["submit_page"]
        self.messagebox_language = self.controller.interface_language["messagebox"]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Submit
        self.controller.style.configure("my.info.Outline.TButton", font=(None, 18))
        self.submit_button = ttk.Button(
            self,
            text=self.submit_page_language["submit_button"],
            command=self.submit,
        )
        self.submit_button.config(style="my.info.Outline.TButton")

        # Feedback
        self.feedback_label = tk.Label(self, text=self.submit_page_language["feedback_label"])
        self.feedback_label.bind(
            "<Button-1>",
            lambda e: self.send_feedback(self.submit_page_language["send_feedback_email_subject"]),  # noqa: ARG005
        )

        # Grid
        self.submit_button.grid(row=0, column=0, ipadx=20, ipady=12, padx=10, pady=(18, 8), sticky="n")
        self.feedback_label.grid(row=1, column=0, padx=10, pady=(8, 18), sticky="s")

    def submit(self: SubmitPage) -> None:
        """Collects the necessary data from all the pages and sends it to the generator function."""
        # Class
        class_ = self.controller.topic_page.class_stringvar.get()
        subject = self.controller.topic_page.subject_stringvar.get()
        topic = self.controller.topic_page.topic_stringvar.get()
        student_indices = self.controller.student_page.student_listbox.curselection()  # type: ignore [no-untyped-call]
        students = [self.controller.student_page.student_listbox.get(index) for index in student_indices]
        online_evaluator = self.controller.data_page.online_evaluator_booleanvar.get()
        date = self.controller.data_page.date_entry.entry.get()
        question_number = self.controller.question_page.question_number_spinbox.get()
        random_question_order = self.controller.question_page.random_question_order_booleanvar.get()
        random_option_order = self.controller.question_page.random_option_order_booleanvar.get()

        if not (
            self.controller.validator.validate_class(class_)
            and self.controller.validator.validate_subject(subject)
            and self.controller.validator.validate_topic(topic)
            and self.controller.validator.validate_students(students)
            and self.controller.validator.validate_date(date)
            and self.controller.validator.validate_question_number(question_number)
        ):
            return

        checkmark_fields = CheckmarkFields(
            class_=class_,
            subject=subject,
            topic=topic,
            students=students,
            online_evaluator=online_evaluator,
            date=date,
            question_number=int(question_number),
            random_question_order=random_question_order,
            random_option_order=random_option_order,
        )

        try:
            generate_assessment(checkmark_fields)
            open_folder = messagebox.askquestion(
                title="Siker!",
                message="A dolgozatok elkészültek. Szeretnéd megnyitni a mappát?",
                icon="question",
            )
            if open_folder == "yes":
                # Changing askquestion message box button text is a lot of extra effort.
                self.open_generated_documents_folder(
                    f"data/generated/{checkmark_fields.date}_{checkmark_fields.subject}_{checkmark_fields.class_}",
                )

        # TODO: Look for specific exceptions
        except Exception as exception:  # noqa: BLE001
            messagebox.showerror(
                title="Hiba!",
                message=f"Hiba történt a dolgozatok elkészítése során:\n{exception}",
                icon="error",
            )

    @staticmethod
    def open_generated_documents_folder(path: str) -> None:
        """Opens the folder where the generated documents are stored."""
        system_platform = platform.system()
        if system_platform == "Windows":
            os.startfile(path)  # type: ignore [attr-defined]  # noqa: S606
        elif system_platform == "Darwin":
            subprocess.Popen(["open", path])  # noqa: S603, S607
        else:
            subprocess.Popen(["xdg-open", path])  # noqa: S603, S607

    @staticmethod
    def send_feedback(subject: str) -> None:
        """Opens the default mail client to send feedback."""
        recipient = "info@pythonvilag.hu"
        webbrowser.open("mailto:?to=" + recipient + "&subject=" + subject, new=1)


class InterfaceValidation:
    """Collection of functions to validate the data entered by the user."""

    def __init__(self: InterfaceValidation, controller: GeneratorInterface) -> None:
        """Constructor of the InterfaceValidation class.

        Args:
            self (InterfaceValidation): The InterfaceValidation object.
            controller (GeneratorInterface): The GeneratorInterface object.
        """
        self.controller = controller
        self.interface_language = self.controller.interface_language

    def validate_class(self: InterfaceValidation, class_: str) -> bool:
        """Validates the class field."""
        if class_ == self.interface_language["topic_page"]["class_stringvar"]:
            self._show_missing_field_error(self.interface_language["messagebox"]["missing_class_label"])
            return False
        return True

    def validate_subject(self: InterfaceValidation, subject: str) -> bool:
        """Validates the subject field."""
        if subject == self.interface_language["topic_page"]["subject_stringvar"]:
            self._show_missing_field_error(self.interface_language["messagebox"]["missing_subject_label"])
            return False
        return True

    def validate_topic(self: InterfaceValidation, topic: str) -> bool:
        """Validates the topic field."""
        if topic == self.interface_language["topic_page"]["topic_stringvar"]:
            self._show_missing_field_error(self.interface_language["messagebox"]["missing_topic_label"])
            return False
        return True

    def validate_students(self: InterfaceValidation, students: list[str]) -> bool:
        """Validates the students field."""
        if not students:
            self._show_missing_field_error(self.interface_language["messagebox"]["missing_students"])
            return False
        return True

    def validate_date(self: InterfaceValidation, date: str) -> bool:
        """Validates the date field."""
        if not date:
            self._show_missing_field_error(self.interface_language["messagebox"]["missing_date_label"])
            return False
        return True

    def validate_question_number(self: InterfaceValidation, question_number: str) -> bool:
        """Validates that the number of questions is an integer between 1 and 20."""
        if not question_number:
            self._show_missing_field_error(self.interface_language["messagebox"]["missing_question_number"])
            return False
        try:
            int(question_number)
        except ValueError:
            messagebox.showerror(
                title="Hibás adat",
                message="A kérdések száma csak egész szám lehet!",
                icon="error",
            )
            return False
        # TODO: Check against the total number of questions instead of 20
        if not (1 <= int(question_number) <= 20):  # noqa: PLR2004
            messagebox.showerror(
                title="Hibás adat",
                message="A kérdések száma csak 1 és 20 közötti érték lehet!",
                icon="error",
            )
            return False
        return True

    def _show_missing_field_error(self: InterfaceValidation, missing_field_name: str) -> None:
        """Shows an error message if a field is missing."""
        messagebox.showerror(
            title="Hiányzó adat",
            message=f"Kérlek add meg a(z) {missing_field_name} mezőt!",
            icon="error",
        )

    def validate_student_number(self: InterfaceValidation, student_number: str, available_students: list[str]) -> bool:
        """Validates that the student number is an integer between 1 and the number of students."""
        if not self.validate_available_students(available_students):
            return False
        try:
            student_number_int = int(student_number)
        except ValueError:
            messagebox.showerror(
                title="Hibás adat",
                message="A sorsolt diák szám csak egész szám lehet!",
                icon="error",
            )
            return False
        if student_number_int < 1 or student_number_int > len(available_students):
            messagebox.showerror(
                title="Hibás adat",
                message="A sorsolt diák szám csak 1 és az összes diák száma közötti érték lehet!",
                icon="error",
            )
            return False
        return True

    @staticmethod
    def validate_available_students(available_students: list[str]) -> bool:
        """Validates that the list of available students is not empty."""
        if not available_students:
            messagebox.showerror(
                title="Hiányzó adat",
                message="Kérlek először add meg az osztály mezőt!",
                icon="error",
            )
            return False
        return True

    def validate_online_evaluator_connection(self: InterfaceValidation) -> bool:
        """Validates that the program can connect to the internet and the checkmark server."""
        if not self._validate_connection("http://google.com"):
            messagebox.showerror(
                title="Hálózati hiba",
                message="Nem sikerült csatlakozni az internethez.",
                icon="error",
            )
            return False

        if not self._validate_connection("http://127.0.0.1:5000/checkmark/register-pocket/"):
            # TODO: Update URL to final address
            messagebox.showerror(
                title="Hálózati hiba",
                message="Nem sikerült csatlakozni a szerverhez.",
                icon="error",
            )
            return False
        return True

    @staticmethod
    def _validate_connection(url: str) -> bool:
        """Validates that the program can connect to the given URL."""
        ok_response = 200
        try:
            response = requests.get(url, timeout=5)
        except requests.exceptions.ConnectionError:
            return False
        if response.status_code != ok_response:
            return False
        return True

"""
Graphical User Interface for evaluating the images of the assessments generated with Checkmark.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import tkinter as tk

from ttkbootstrap import Style


class EvaluatorInterface(tk.Tk):
    """
    Graphical User Interface for assessment evaluation.
    """

    def __init__(self) -> None:
        # TODO: Support multiple languages
        tk.Tk.__init__(self)
        self.iconphoto(True, tk.PhotoImage(file="data/app/icon_e.png"))
        window_width = 680
        window_height = 440
        top_left_x = (self.winfo_screenwidth() - window_width) // 2
        top_left_y = (self.winfo_screenheight() - window_height) // 2

        self.wm_title("Checkmark Evaluator")
        self.wm_geometry(f"{window_width}x{window_height}+{top_left_x}+{top_left_y}")
        self.wm_resizable(False, False)
        self.style = Style(theme="superhero")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

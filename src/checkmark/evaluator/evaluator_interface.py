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

from checkmark.evaluator.evaluate import evaluate_assessment


class EvaluatorInterface(tk.Tk):
    def __init__(self) -> None:
        tk.Tk.__init__(self)
        window_width = 680
        window_height = 440

        # TODO: Add icon
        self.wm_title("Checkmark Evaluator")
        self.wm_geometry(f"{window_width}x{window_height}+200+200")
        self.wm_resizable(False, False)
        self.style = Style(theme="superhero")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

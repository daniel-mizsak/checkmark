"""
Init file for checkmark package.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import importlib.metadata
import locale

try:
    locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_ALL, "C.UTF-8")

__version__ = importlib.metadata.version("checkmark-assistant")


# Variables for submodules
# BASE_URL = "https://pythonvilag.hu/checkmark"  # noqa: ERA001
BASE_URL = "http://127.0.0.1:5000/checkmark/"
REGISTER_POCKET_ENDPOINT = "/register-pocket"

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

__version__ = importlib.metadata.version("checkmark")

"""
Init file for checkmark package.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import importlib.metadata
import os

os.environ["LC_ALL"] = "hu_HU.UTF-8"
__version__ = importlib.metadata.version("checkmark")

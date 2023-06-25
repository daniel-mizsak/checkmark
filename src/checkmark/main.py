from __future__ import annotations

import argparse
import importlib.metadata

from checkmark.evaluator.evaluator_interface import EvaluatorInterface
from checkmark.generator.generator_interface import GeneratorInterface


def parse_arguments() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        action="store_true",
        help="Version",
        required=False,
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Graphical User Interface for Assessment Generation",
        required=False,
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Graphical User Interface for Assessment Evaluation",
        required=False,
    )

    args = parser.parse_args()
    return args


def main() -> bool:
    """Main function of the checkmark application."""
    args = parse_arguments()

    if args.version:
        print(f"Checkmark v{importlib.metadata.version('checkmark')}")
        return True

    if args.generate:
        GeneratorInterface().mainloop()
        return True

    if args.evaluate:
        EvaluatorInterface().mainloop()
        return True

    return False

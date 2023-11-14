"""
Main module of the checkmark application.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

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

    subparsers = parser.add_subparsers(title="Commands", dest="command")

    generate_parser = subparsers.add_parser("generate", help="Graphical User Interface for Assessment Generation")
    generate_parser.add_argument(
        "--language",
        type=str,
        help="Interface language",
        required=False,
        default="HUN",
        choices=["HUN", "ENG"],
    )

    subparsers.add_parser("evaluate", help="Graphical User Interface for Assessment Evaluation")

    args = parser.parse_args()
    return args


def main() -> bool:
    """Main function of the checkmark application."""
    args = parse_arguments()

    if args.version:
        print(f"Checkmark v{importlib.metadata.version('checkmark')}")
        return True

    if args.command is None:
        print("No command given. Use --help for more information.")
        return False

    if args.command == "generate":
        GeneratorInterface(args.language).mainloop()
        return True

    if args.command == "evaluate":
        EvaluatorInterface().mainloop()
        return True

    return False

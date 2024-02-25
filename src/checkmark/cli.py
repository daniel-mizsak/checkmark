"""
Command Line Interface for the Checkmark application.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import argparse
import importlib.metadata
import sys

from checkmark.evaluator.evaluator_interface import EvaluatorInterface
from checkmark.generator.generator_interface import GeneratorInterface


def _parse_arguments() -> argparse.Namespace:
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

    return parser.parse_args()


def main() -> int:
    """Main function of the checkmark application."""
    args = _parse_arguments()

    if args.version:
        print(f"Checkmark v{importlib.metadata.version('checkmark-assistant')}")  # noqa: T201
        return 0

    if args.command == "generate":
        GeneratorInterface(args.language).mainloop()
        return 0

    if args.command == "evaluate":
        EvaluatorInterface().mainloop()
        return 0

    print("Error! No command given. Use --help for more information.", file=sys.stderr)  # noqa: T201
    return 1

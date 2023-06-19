import argparse
import importlib.metadata

from checkmark.evaluator.evaluator_interface import EvaluatorInterface
from checkmark.generator.generator_interface import GeneratorInterface


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        action="store_true",
        help="Version",
        required=False,
    )
    parser.add_argument(
        "--generator",
        action="store_true",
        help="Graphical User Interface for Assessment Generation",
        required=False,
    )
    parser.add_argument(
        "--evaluator",
        action="store_true",
        help="Graphical User Interface for Assessment Evaluation",
        required=False,
    )

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    if args.version:
        print(f"Checkmark v{importlib.metadata.version('checkmark')}")
        return 0

    if args.generator:
        GeneratorInterface().mainloop()
        return 0

    if args.evaluator:
        EvaluatorInterface().mainloop()
        return 0

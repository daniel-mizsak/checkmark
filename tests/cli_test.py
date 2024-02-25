import importlib.metadata
import subprocess


def test_version_command() -> None:
    result = subprocess.run(["checkmark", "--version"], capture_output=True, text=True)  # noqa: PLW1510, S603, S607
    assert not result.stderr
    assert result.stdout == f"Checkmark v{importlib.metadata.version('checkmark-assistant')}\n"


def test_empty_command() -> None:
    result = subprocess.run(["checkmark"], capture_output=True, text=True)  # noqa: PLW1510, S603, S607
    assert result.stderr == "Error! No command given. Use --help for more information.\n"
    assert result.stdout == ""

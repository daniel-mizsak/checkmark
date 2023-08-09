from checkmark.generator.generator_interface import InterfaceValidation


def test_validate_email() -> None:
    validator = InterfaceValidation()
    assert validator._validate_email("name@domail.com") is True
    assert validator._validate_email("name@domail") is False

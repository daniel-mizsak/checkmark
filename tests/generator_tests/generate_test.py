from checkmark.generator.generate import (
    PocketData,
    _generate_pocket_data,
    _send_pocket_data,
)


def test_generate_pocket_data() -> None:
    students = ["John Doe", "Jane Doe"]
    date = "2042-01-01"
    pocket_data = _generate_pocket_data(students, date)
    assert isinstance(pocket_data, PocketData)
    assert pocket_data.students == students
    assert pocket_data.date == date
    assert pocket_data.pocket_id.isalnum()
    assert len(pocket_data.pocket_id) == 20
    assert pocket_data.pocket_password.isalpha()
    assert len(pocket_data.pocket_password) == 8


def test_send_pocket_data() -> None:
    students = ["John Doe", "Jane Doe"]
    date = "2042-01-01"
    pocket_data = _generate_pocket_data(students, date)
    assert not _send_pocket_data(pocket_data)

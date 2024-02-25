from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture(scope="session")
def temp_excel_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    excel_path = Path(tmp_path_factory.mktemp("data"))
    df_correct = pd.DataFrame(
        {
            "Feladat sorszám": [1, 2, 3],
            "Kérdés": ["Kérdés 1", "Kérdés 2", "Kérdés 3"],
            "A": ["A1", "A2", "A3"],
            "B": ["B1", "B2", "B3"],
            "C": ["C1", "C2", "C3"],
            "D": ["D1", "D2", "D3"],
            "Megoldás": ["A", "B", "C"],
        }
    )
    df_correct.to_excel(excel_path / "correct.xlsx", index=False)
    df_reoccurring_index = pd.DataFrame(
        {
            "Feladat sorszám": [1, 1, 2],
            "Kérdés": ["Kérdés 1", "Kérdés 1", "Kérdés 2"],
            "A": ["A1", "A1", "A2"],
            "B": ["B1", "B1", "B2"],
            "C": ["C1", "C1", "C2"],
            "D": ["D1", "D1", "D2"],
            "Megoldás": ["A", "A", "B"],
        }
    )
    df_reoccurring_index.to_excel(excel_path / "reoccurring_index.xlsx", index=False)

    df_unexpected_correct_value = pd.DataFrame(
        {
            "Feladat sorszám": [1, 2, 3],
            "Kérdés": ["Kérdés 1", "Kérdés 2", "Kérdés 3"],
            "A": ["A1", "A2", "A3"],
            "B": ["B1", "B2", "B3"],
            "C": ["C1", "C2", "C3"],
            "D": ["D1", "D2", "D3"],
            "Megoldás": ["A", "B", "X"],
        }
    )
    df_unexpected_correct_value.to_excel(excel_path / "unexpected_correct_value.xlsx", index=False)

    return excel_path

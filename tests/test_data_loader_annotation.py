from io import StringIO

import pandas as pd
import pytest

from app.data_loader import ExpressionDataManager

VALID_CSV = """AGI;Name
AT1G01010;GeneA
AT1G01020;GeneB
"""

VALID_CSV_WITH_SPACE = """AGI;Name
AT1G01010;DNA-RNA polymerase, subunit M, archaeal
"""

VALID_CSV_WITH_ESCAPED_SEMICOLON = """AGI;Name
AT1G01010;"RABA3;RAB GTPase homolog A3"
"""

INVALID_CSV = """GeneID;GeneName
AT1G01010;GeneA
"""

@pytest.fixture(autouse=True)
def reset_singleton():
    ExpressionDataManager._instance = None

def create_manager_from_string(csv_string):
    manager = ExpressionDataManager()
    manager._annotation_path = StringIO(csv_string)
    return manager

def test_valid_simple_csv():
    manager = create_manager_from_string(VALID_CSV)
    df = manager.load_annotation_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "AGI" in df.columns
    assert "Name" in df.columns
    assert df.iloc[0, 0] == "AT1G01010"
    assert df.iloc[0, 1] == "GeneA"


def test_valid_csv_with_spaces():
    manager = create_manager_from_string(VALID_CSV_WITH_SPACE)
    df = manager.load_annotation_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.iloc[0,0] == "AT1G01010"
    assert df.iloc[0,1] == "DNA-RNA polymerase, subunit M, archaeal"

def test_valid_csv_with_escaped_semicolon():
    manager = create_manager_from_string(VALID_CSV_WITH_ESCAPED_SEMICOLON)
    df = manager.load_annotation_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.iloc[0,0] == "AT1G01010"
    assert df.iloc[0,1] == "RABA3;RAB GTPase homolog A3"

def test_load_annotation_data_invalid():
    with pytest.raises(ValueError, match="CSV must contain columns"):
        manager = create_manager_from_string(INVALID_CSV)
        df = manager.load_annotation_data()

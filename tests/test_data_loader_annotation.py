from io import StringIO

import pandas as pd
import pytest

from app.data_loader import load_annotation_data

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

def test_valid_simple_csv():
    df = load_annotation_data(StringIO(VALID_CSV))
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "AGI" in df.columns
    assert "Name" in df.columns
    assert df.iloc[0, 0] == "AT1G01010"
    assert df.iloc[0, 1] == "GeneA"


def test_valid_csv_with_spaces():
    df = load_annotation_data(StringIO(VALID_CSV_WITH_SPACE))
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.iloc[0,0] == "AT1G01010"
    assert df.iloc[0,1] == "DNA-RNA polymerase, subunit M, archaeal"

def test_valid_csv_with_escaped_semicolon():
    df = load_annotation_data(StringIO(VALID_CSV_WITH_ESCAPED_SEMICOLON))
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.iloc[0,0] == "AT1G01010"
    assert df.iloc[0,1] == "RABA3;RAB GTPase homolog A3"

def test_load_annotation_data_invalid():
    with pytest.raises(ValueError, match="CSV must contain columns"):
        load_annotation_data(StringIO(INVALID_CSV))

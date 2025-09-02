from unittest.mock import patch

import dash.html as html
import pandas as pd
import pytest

from app.layout import create_layout


@patch('app.layout.load_annotation_data')
@patch("app.layout.load_quant_data")
def test_layout_contains_correct_elements(mock_ann, mock_quant):
    mock_ann.return_value = pd.DataFrame({
        "AGI": [],
        "Name": []
    })
    mock_quant.return_value = pd.DataFrame()
    layout = create_layout("does_not_exist", "does_not_exist")
    assert isinstance(layout, html.Div)
    ids = [child.id for child in layout.children if hasattr(child, "id")]
    assert "expression-plot" in ids
    assert "gene-selector" in ids

@patch("app.layout.load_quant_data")
@patch('app.layout.load_annotation_data')
def test_dropdown_contains_correct_values(mock_ann, mock_quant):
    mock_ann.return_value = pd.DataFrame({
        "AGI": ["AT1G01010", "AT1G01020"],
        "Name": ["GeneA", "GeneB"]
    })
    mock_quant.return_value = pd.DataFrame()

    layout = create_layout("does_not_exist", "does_not_exist")
    dropdown = next(c for c in layout.children
                    if getattr(c, "id", None) == "gene-selector")

    assert mock_ann.called

    expected_labels = ["AT1G01010; GeneA", "AT1G01020; GeneB"]
    actual_labels = [opt["label"] for opt in dropdown.options]

    assert actual_labels == expected_labels

    expected_values = ["AT1G01010", "AT1G01020"]
    actual_values = [opt["value"] for opt in dropdown.options]
    assert actual_values == expected_values


@patch('app.layout.load_quant_data')
@patch('app.layout.load_annotation_data')
def test_dropdown_missing_name_column(mock_ann, mock_quant):
    mock_ann.return_value = pd.DataFrame({
        "AGI": ["AT1G01010", "AT1G01020"]
    })
    mock_quant.return_value = pd.DataFrame()

    with pytest.raises(KeyError, match="Name"):
        create_layout("fake_path", "fake_path")


@patch('app.layout.load_quant_data')
@patch('app.layout.load_annotation_data')
def test_dropdown_missing_agi_column(mock_ann, mock_quant):
    mock_ann.return_value = pd.DataFrame({
        "Name": ["GeneA", "GeneB"]
    })
    mock_quant.return_value = pd.DataFrame()

    with pytest.raises(KeyError, match="AGI"):
        create_layout("fake_path", "fake_path")


@patch('app.layout.load_quant_data')
@patch('app.layout.load_annotation_data')
def test_dropdown_null_gene_names(mock_ann, mock_quant):
    mock_ann.return_value = pd.DataFrame({
        "AGI": ["AT1G01010", "AT1G01020"],
        "Name": ["GeneA", None]
    })
    mock_quant.return_value = pd.DataFrame()

    layout = create_layout("fake_path", "fake_path")
    dropdown = next(c for c in layout.children
                    if getattr(c, "id", None) == "gene-selector")

    expected_labels = ["AT1G01010; GeneA", "AT1G01020; Unknown"]
    actual_labels = [opt["label"] for opt in dropdown.options]

    assert actual_labels == expected_labels



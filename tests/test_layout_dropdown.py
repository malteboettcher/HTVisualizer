from unittest.mock import MagicMock, patch

import dash.html as html
import pandas as pd
import pytest

from app.data_loader import ExpressionDataManager
from app.layout import create_layout


def make_mock_manager(annotation_df=None, quant_df=None):
    manager = MagicMock(spec=ExpressionDataManager)
    manager.load_annotation_data.return_value = annotation_df \
        if annotation_df is not None else pd.DataFrame()
    manager.load_quant_data.return_value =  quant_df \
        if quant_df is not None else pd.DataFrame()
    return manager


@patch("app.layout.ExpressionDataManager", autospec=True)
def test_layout_contains_correct_elements(mock_manager_cls):
    mock_manager = make_mock_manager()
    mock_manager_cls.return_value = mock_manager

    layout = create_layout("does_not_exist", "does_not_exist")
    assert isinstance(layout, html.Div)
    ids = [child.id for child in layout.children if hasattr(child, "id")]
    assert "expression-plot" in ids
    assert "gene-selector" in ids


@patch("app.layout.ExpressionDataManager", autospec=True)
def test_dropdown_contains_correct_values(mock_manager_cls):
    annotation_df = pd.DataFrame({
        "AGI": ["AT1G01010", "AT1G01020"],
        "Name": ["GeneA", "GeneB"]
    })
    mock_manager = make_mock_manager(annotation_df=annotation_df)
    mock_manager_cls.return_value = mock_manager

    layout = create_layout("does_not_exist", "does_not_exist")
    dropdown = next(c for c in layout.children
                    if getattr(c, "id", None) == "gene-selector")

    expected_labels = ["AT1G01010; GeneA", "AT1G01020; GeneB"]
    actual_labels = [opt["label"] for opt in dropdown.options]
    assert actual_labels == expected_labels

    expected_values = ["AT1G01010", "AT1G01020"]
    actual_values = [opt["value"] for opt in dropdown.options]
    assert actual_values == expected_values


@patch("app.layout.ExpressionDataManager", autospec=True)
def test_dropdown_missing_name_column(mock_manager_cls):
    annotation_df = pd.DataFrame({
        "AGI": ["AT1G01010", "AT1G01020"]
    })
    mock_manager = make_mock_manager(annotation_df=annotation_df)
    mock_manager_cls.return_value = mock_manager

    with pytest.raises(KeyError, match="Name"):
        create_layout("fake_path", "fake_path")

@patch("app.layout.ExpressionDataManager", autospec=True)
def test_dropdown_missing_agi_column(mock_manager_cls):
    annotation_df = pd.DataFrame({
        "Name": ["GeneA", "GeneB"]
    })
    mock_manager = make_mock_manager(annotation_df=annotation_df)
    mock_manager_cls.return_value = mock_manager

    with pytest.raises(KeyError, match="AGI"):
        create_layout("fake_path", "fake_path")

@patch("app.layout.ExpressionDataManager", autospec=True)
def test_dropdown_null_gene_names(mock_manager_cls):
    annotation_df = pd.DataFrame({
        "AGI": ["AT1G01010", "AT1G01020"],
        "Name": ["GeneA", None]
    })
    mock_manager = make_mock_manager(annotation_df=annotation_df)
    mock_manager_cls.return_value = mock_manager

    layout = create_layout("fake_path", "fake_path")
    dropdown = next(c for c in layout.children
                    if getattr(c, "id", None) == "gene-selector")

    expected_labels = ["AT1G01010; GeneA", "AT1G01020; Unknown"]
    actual_labels = [opt["label"] for opt in dropdown.options]
    assert actual_labels == expected_labels



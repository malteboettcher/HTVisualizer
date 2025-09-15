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
    ids =  _collect_ids(layout.children)
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
    dropdown = _find_component_by_id(layout.children, "gene-selector")
    assert dropdown is not None, "Dropdown not found in layout"

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

    layout = create_layout("does_not_exist", "does_not_exist")
    dropdown = _find_component_by_id(layout.children, "gene-selector")
    assert dropdown is not None, "Dropdown not found in layout"

    expected_labels = ["AT1G01010; GeneA", "AT1G01020; Unknown"]
    actual_labels = [opt["label"] for opt in dropdown.options]
    assert actual_labels == expected_labels

def _collect_ids(children):
    ids = []
    for child in children:
        if hasattr(child, "id") and child.id is not None:
            ids.append(child.id)
        if hasattr(child, "children"):
            if isinstance(child.children, list):
                ids.extend(_collect_ids(child.children))
            else:
                ids.extend(_collect_ids([child.children]))
    return ids


def _find_component_by_id(children, target_id):
    for child in children:
        if hasattr(child, "id") and child.id == target_id:
            return child
        if hasattr(child, "children"):
            child_list = child.children \
                if isinstance(child.children, list) \
                else [child.children]
            result = _find_component_by_id(child_list, target_id)
            if result is not None:
                return result
    return None



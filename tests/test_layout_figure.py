from collections import defaultdict
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from app.data_loader import ExpressionDataManager
from app.layout import update_expression_plot


@pytest.fixture(autouse=True)
def reset_singleton():
    ExpressionDataManager._instance = None
    ExpressionDataManager._expression_data = None
    ExpressionDataManager._annotation_data = None


@pytest.fixture
def sample_expression_data():
    isoforms = ['GENE1.1', 'GENE1.2', 'GENE2.1']
    stats = ['mean', 'std']
    row_index = pd.MultiIndex.from_product([isoforms, stats],
                                           names=['isoform', 'statistic'])

    columns = ['sample_WT_rep1', 'sample_WT_rep2', 'sample_KO_rep1', 'sample_KO_rep2']

    np.random.seed(42)
    data = np.random.rand(len(row_index), len(columns)) * 100
    return pd.DataFrame(data, index=row_index, columns=columns)

@pytest.fixture
def mock_data_manager(sample_expression_data):
    manager = Mock(spec=ExpressionDataManager)
    manager.load_quant_data.return_value = sample_expression_data
    manager.get_sample_groups.return_value = list(sample_expression_data.columns)
    manager.get_groups_by_genotype.return_value = {
        'WT': ['sample_WT_rep1', 'sample_WT_rep2'],
        'KO': ['sample_KO_rep1', 'sample_KO_rep2']
    }

    def mock_get_isoforms(gene):
        if gene == 'GENE1':
            return ['GENE1.1', 'GENE1.2']
        elif gene == 'GENE2':
            return ['GENE2.1']
        else:
            return []

    manager.get_isoforms_for_gene.side_effect = mock_get_isoforms
    return manager

def test_empty_gene_selector_returns_empty_fig(mock_data_manager):
    with patch('app.layout.ExpressionDataManager', return_value=mock_data_manager):
        result = update_expression_plot(None)
        assert "No data to display" == result.layout.annotations[0].text


def test_no_matching_isoforms_returns_empty_fig(mock_data_manager):
    with patch('app.layout.ExpressionDataManager', return_value=mock_data_manager):
        result = update_expression_plot("GENE3")

        assert "No expression data found for GENE3" == result.layout.annotations[0].text


def test_successful_plot_generation_single_isoform(mock_data_manager):
    with patch('app.layout.ExpressionDataManager', return_value=mock_data_manager):
        result = update_expression_plot("GENE2")

        mock_data_manager.load_quant_data.assert_called_once()
        mock_data_manager.get_isoforms_for_gene.assert_called_once_with("GENE2")
        mock_data_manager.get_sample_groups.assert_called_once()
        mock_data_manager.get_groups_by_genotype.assert_called_once()
        assert isinstance(result, go.Figure)

        # Should have 2 traces (1 isoform x 2 genotypes)
        assert len(result.data) == 2
        assert result.layout.title.text == "Expression Profile: GENE2"
        assert result.layout.yaxis.title.text == "mean/SD TPM"



def test_successful_plot_generation_multiple_isoforms(mock_data_manager):
    with patch('app.layout.ExpressionDataManager', return_value=mock_data_manager):
        result = update_expression_plot("GENE1")

        mock_data_manager.load_quant_data.assert_called_once()
        mock_data_manager.get_isoforms_for_gene.assert_called_once_with("GENE1")
        mock_data_manager.get_sample_groups.assert_called_once()
        mock_data_manager.get_groups_by_genotype.assert_called_once()
        assert isinstance(result, go.Figure)

        # Should have 4 traces (2 isoforms x 2 genotypes)
        assert len(result.data) == 4
        assert result.layout.title.text == "Expression Profile: GENE1"
        assert result.layout.yaxis.title.text == "mean/SD TPM"


def test_legend_entries(mock_data_manager):
    with patch('app.layout.ExpressionDataManager', return_value=mock_data_manager):
        result = update_expression_plot("GENE1")

        assert isinstance(result, go.Figure)
        assert len(result.data) == 4

        legend_entries = [trace.name for trace in result.data if trace.showlegend]

        assert legend_entries == ['GENE1.1', 'GENE1.2']

def test_consistent_colors_across_isoforms(mock_data_manager):
    with patch('app.layout.ExpressionDataManager', return_value=mock_data_manager):
        result = update_expression_plot("GENE1")

        assert isinstance(result, go.Figure)

        assert len(result.data) == 4

        colors_by_isoform = defaultdict(set)
        for trace in result.data:
            colors_by_isoform[trace.name].add(trace.line.color)

        for isoform, colors in colors_by_isoform.items():
            assert len(colors) == 1

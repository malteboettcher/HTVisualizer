from unittest.mock import patch

import plotly.graph_objects as go
import pytest

from app.layout import download_pdf, download_png, download_svg

sample_gene = "AT1G01010"

@pytest.fixture
def sample_figure():
    """Create a sample figure for testing"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[1, 2, 3, 4],
        y=[10, 11, 12, 13],
        mode='lines+markers',
        name='Test Data'
    ))
    fig.update_layout(
        title='Test Plot',
        xaxis_title='X Axis',
        yaxis_title='Y Axis'
    )
    return fig.to_dict()


def test_download_svg_none_clicks(sample_figure):
    result = download_svg(None, sample_figure, sample_gene)
    assert result is None

def test_download_svg_no_clicks(sample_figure):
    result = download_svg(0, sample_figure, sample_gene)
    assert result is None

def test_download_svg_no_figure():
    result = download_svg(1, None, sample_gene)
    assert result is None

@patch('plotly.io.to_image')
def test_download_svg_success(mock_to_image, sample_figure):
    mock_svg_content = b'<svg>test svg content</svg>'
    mock_to_image.return_value = mock_svg_content

    result = download_svg(1, sample_figure, sample_gene)

    assert isinstance(result, dict)
    assert result['content'] == mock_svg_content
    assert result['filename'] == f"expression_plot_{sample_gene}.svg"
    assert result['type'] == "image/svg+xml"

    mock_to_image.assert_called_once()
    call_args = mock_to_image.call_args
    assert call_args[1]['format'] == 'svg'
    assert call_args[1]['width'] == 1600
    assert call_args[1]['height'] == 550

@patch('plotly.io.to_image')
def test_download_svg_no_gene_name(mock_to_image, sample_figure):
    mock_svg_content = b'<svg>test svg content</svg>'
    mock_to_image.return_value = mock_svg_content

    result = download_svg(1, sample_figure, None)

    assert result['filename'] == "expression_plot_plot.svg"

def test_download_png_none_clicks(sample_figure):
    result = download_png(None, sample_figure, sample_gene)
    assert result is None

def test_download_png_no_clicks(sample_figure):
    # Test with 0 clicks
    result = download_png(0, sample_figure, sample_gene)
    assert result is None

def test_download_png_no_figure():
    result = download_png(1, None, sample_gene)
    assert result is None

@patch('plotly.io.to_image')
def test_download_png_success(mock_to_image, sample_figure):
    mock_png_content = b'fake png binary data'
    mock_to_image.return_value = mock_png_content

    result = download_png(1, sample_figure, sample_gene)

    assert isinstance(result, dict)
    assert result['content'] == mock_png_content
    assert result['filename'] == f"expression_plot_{sample_gene}.png"
    assert result['type'] == "image/png"

    mock_to_image.assert_called_once()
    call_args = mock_to_image.call_args
    assert call_args[1]['format'] == 'png'
    assert call_args[1]['width'] == 1600
    assert call_args[1]['height'] == 550
    assert call_args[1]['scale'] == 2

@patch('plotly.io.to_image')
def test_download_png_no_gene_name(mock_to_image, sample_figure):
    mock_png_content = b'fake png binary data'
    mock_to_image.return_value = mock_png_content

    result = download_png(1, sample_figure, None)

    assert result['filename'] == "expression_plot_plot.png"

def test_download_pdf_none_clicks(sample_figure):
    result = download_pdf(None, sample_figure, sample_gene)
    assert result is None

def test_download_pdf_no_clicks(sample_figure):
    result = download_pdf(0, sample_figure, sample_gene)
    assert result is None

def test_download_pdf_no_figure():
    result = download_pdf(1, None, sample_gene)
    assert result is None

@patch('plotly.io.to_image')
def test_download_pdf_success(mock_to_image, sample_figure):
    mock_pdf_content = b'fake pdf binary data'
    mock_to_image.return_value = mock_pdf_content

    result = download_pdf(1, sample_figure, sample_gene)

    assert isinstance(result, dict)
    assert result['content'] == mock_pdf_content
    assert result['filename'] == f"expression_plot_{sample_gene}.pdf"
    assert result['type'] == "application/pdf"

    mock_to_image.assert_called_once()
    call_args = mock_to_image.call_args
    assert call_args[1]['format'] == 'pdf'
    assert call_args[1]['width'] == 1600
    assert call_args[1]['height'] == 550

@patch('plotly.io.to_image')
def test_download_pdf_no_gene_name(mock_to_image, sample_figure):
    mock_pdf_content = b'fake pdf binary data'
    mock_to_image.return_value = mock_pdf_content

    result = download_pdf(1, sample_figure, None)

    assert result['filename'] == "expression_plot_plot.pdf"

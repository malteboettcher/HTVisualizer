import base64

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from dash import Input, Output, State, callback, dcc, html

from app.data_loader import ExpressionDataManager


def create_layout(annotation_path, expression_path):
    data_manager = ExpressionDataManager(
        annotation_path=annotation_path,
        quant_path=expression_path
    )
    annotation_data = data_manager.load_annotation_data()
    data_manager.load_quant_data()

    fig = _empty_fig()
    dropdown_options = [
        {
            "label":
                f"{row['AGI']}; {row['Name'] if pd.notna(row['Name']) else 'Unknown'}",
            "value": row['AGI']
        }
        for _, row in annotation_data.iterrows()
    ]

    layout = html.Div([
        dbc.NavbarSimple(
            brand="RNA-seq Expression Dashboard",
            brand_href="#",
            color="primary",
            dark=True,
            className="mb-3"
        ),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Label("Gene Selection",
                                       className="form-label fw-bold mb-2"),
                            dcc.Dropdown(
                                id="gene-selector",
                                options=dropdown_options,
                                searchable=True,
                                placeholder="Type to search genes...",
                                className="mb-0"
                            ),
                            html.Label("Export Options",
                                       className="form-label fw-bold mb-2 mt-2"),
                            html.Div(
                                dbc.ButtonGroup([
                                    dbc.Button(
                                        [html.I(className="fas fa-download me-2"),
                                         "SVG"],
                                        id="download-svg-btn",
                                        color="outline-primary",
                                        size="sm",
                                        className="mb-2 w-100",
                                        disabled=True
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-download me-2"),
                                         "PNG"],
                                        id="download-png-btn",
                                        color="outline-secondary",
                                        size="sm",
                                        className="mb-2 w-100",
                                        disabled=True
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-download me-2"),
                                         "PDF"],
                                        id="download-pdf-btn",
                                        color="outline-success",
                                        size="sm",
                                        className="mb-2 w-100",
                                        disabled=True
                                    ),
                                ], size="sm"),
                            ),
                            dcc.Download(id="download-svg"),
                            dcc.Download(id="download-png"),
                            dcc.Download(id="download-pdf"),
                        ])
                    ], className="shadow-sm border-0")
                ], width=12, lg=3, className="mb-3"),

                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(
                                children=[
                                    dcc.Graph(
                                        id="expression-plot",
                                        figure=fig,
                                        style={"height": "550px"},
                                        config={
                                            'displayModeBar': True,
                                            'displaylogo': False,
                                            "toImageButtonOptions": {
                                                "format": "svg",
                                                "filename": "expression_plot",
                                                "height": 550,
                                                "width": 1600,
                                                "scale": 1
                                            }
                                        },
                                    )
                                ],
                                color="#007bff",
                                type="default"
                            )
                        ], className="p-1")
                    ], className="shadow-sm border-0")
                ], width=12, lg=9)
            ], className="g-3"),

            html.Div(style={"height": "20px"})
        ], fluid=True, className="px-3")
    ])
    return layout

@callback(
    Output("expression-plot", "figure"),
    Input("gene-selector", "value")
)
def update_expression_plot(selected_gene):
    if not selected_gene:
        return _empty_fig()

    data_manager = ExpressionDataManager()
    expression_data = data_manager.load_quant_data()

    matching_isoforms = data_manager.get_isoforms_for_gene(selected_gene)

    if not matching_isoforms:
        return _empty_fig(f"No expression data found for {selected_gene}")

    fig = go.Figure()

    sample_groups = data_manager.get_sample_groups()

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    groups_by_type = data_manager.get_groups_by_genotype()

    x_positions_map = _get_x_positions(groups_by_type)

    all_y = []
    for i, isoform in enumerate(matching_isoforms):
        first_of_type = True
        for _, cols in groups_by_type.items():
            x_values = []
            y_values = []
            error_values = []
            for group in cols:
                mean = expression_data.loc[(isoform, "mean"), group]
                error = expression_data.loc[(isoform, "std"), group]
                all_y.extend([mean + error, mean - error])
                x_values.append(x_positions_map[group])
                y_values.append(mean)
                error_values.append(error)

            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                error_y=dict(
                    type='data',
                    array=error_values,
                    visible=True
                ),
                mode='lines+markers',
                line=dict(width=2, color=colors[i % len(colors)]),
                marker=dict(size=8),
                name=isoform,
                showlegend=first_of_type,
                legendgroup=isoform
            ))
            first_of_type = False

    ymax = max(0, max(all_y) * 1.1)
    ymin = min(0 - max(all_y) * 0.05, min(all_y) * 1.1)
    fig.update_layout(
        title=f'Expression Profile: {selected_gene}',
        yaxis_title="mean/SD TPM",
        height=500,
        showlegend=True,
        yaxis=dict(
            showgrid=True,
            gridcolor="lightgray",
            zeroline=True,
            color='black',
            zerolinecolor="lightgray",
            zerolinewidth=1,
            autorange=False,
            range=[ymin, ymax]
        ),
        xaxis=dict(
            tickvals=[x_positions_map[s] for s in sample_groups],
            ticktext=sample_groups,
            tickangle=45,
            showgrid=True,
            gridcolor="lightgray",
            zeroline=False,
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.01
        ),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig

def _get_x_positions(groups_by_type):
    x_positions_map = {}
    current_pos = 1
    inner_spacing = 0.5
    group_spacing = 0.25
    for _, cols in groups_by_type.items():
        for i, sample in enumerate(cols):
            x_positions_map[sample] = current_pos + i * inner_spacing
        current_pos += len(cols) * inner_spacing + group_spacing
    return x_positions_map


def _empty_fig(message: str = "No data to display"):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, xanchor='center', yanchor='middle',
        showarrow=False, font_size=16
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=500
    )
    return fig


@callback(
    Output("download-svg", "data"),
    Input("download-svg-btn", "n_clicks"),
    State("expression-plot", "figure"),
    State("gene-selector", "value"),
    prevent_initial_call=True,
    running=[
        (Output("download-svg-btn", "disabled"), True, False),
        (Output("download-svg-btn", "children"),
         [dbc.Spinner(size="sm", color="primary"),
          html.Span("Downloading...")],
         [html.I(className="fas fa-download me-2"), "SVG"]),
    ],
)
def download_svg(n_clicks, figure, selected_gene):
    if n_clicks and figure:
        fig = go.Figure(figure)

        svg_string = pio.to_image(fig, format="svg", width=1000, height=400)
        svg_b64 = base64.b64encode(svg_string).decode('utf-8')

        filename = f"expression_plot_{selected_gene or 'plot'}.svg"

        return dict(content=svg_b64, filename=filename, type="image/svg+xml",
                    base64=True)


@callback(
    Output("download-pdf", "data"),
    Input("download-pdf-btn", "n_clicks"),
    State("expression-plot", "figure"),
    State("gene-selector", "value"),
    prevent_initial_call=True,
    running=[
        (Output("download-pdf-btn", "disabled"), True, False),
        (Output("download-pdf-btn", "children"),
         [dbc.Spinner(size="sm", color="primary"),
          html.Span("Downloading...")],
         [html.I(className="fas fa-download me-2"), "PDF"]),
    ],
)
def download_pdf(n_clicks, figure, selected_gene):
    if n_clicks and figure:
        fig = go.Figure(figure)

        pdf_bytes = pio.to_image(fig, format="pdf", width=1000, height=400)
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')

        filename = f"expression_plot_{selected_gene or 'plot'}.pdf"

        return dict(content=pdf_b64, filename=filename, type="application/pdf",
                    base64=True)


@callback(
    Output("download-png", "data"),
    Input("download-png-btn", "n_clicks"),
    State("expression-plot", "figure"),
    State("gene-selector", "value"),
    prevent_initial_call=True,
    running=[
        (Output("download-png-btn", "disabled"), True, False),
        (Output("download-png-btn", "children"),
         [dbc.Spinner(size="sm", color="primary"),
          html.Span("Downloading...")],
         [html.I(className="fas fa-download me-2"), "PNG"]),
    ],
)
def download_png(n_clicks, figure, selected_gene):
    if n_clicks and figure:
        fig = go.Figure(figure)

        png_bytes = pio.to_image(fig, format="png", width=1000, height=400, scale=2)
        png_b64 = base64.b64encode(png_bytes).decode('utf-8')

        filename = f"expression_plot_{selected_gene or 'plot'}.png"

        return dict(content=png_b64, filename=filename, type="image/png", base64=True)



@callback(
    Output("download-svg-btn", "disabled"),
    Output("download-png-btn", "disabled"),
    Output("download-pdf-btn", "disabled"),
    Input("gene-selector", "value")
)
def toggle_download_buttons(selected_gene):
    if not selected_gene:
        return True, True, True
    return False, False, False


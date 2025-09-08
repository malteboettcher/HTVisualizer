import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from app.data_loader import ExpressionDataManager


def create_layout(annotation_path, expression_path):
    data_manager = ExpressionDataManager(
        annotation_path=annotation_path,
        quant_path=expression_path
    )
    annotation_data = data_manager.load_annotation_data()
    data_manager.load_quant_data()


    fig = _empty_fig()

    layout = html.Div(children=[
        html.H1("RNA-seq transcript expression Dashboard"),
        dcc.Dropdown(
            id="gene-selector",
            options=[
                {"label": f"{row['AGI']}; "
                          f"{row['Name'] if pd.notna(row['Name'])else 'Unknown'}",
                 "value": row['AGI']}
                for _, row in annotation_data.iterrows()
            ],
            searchable=True,
            placeholder="Select gene..."
        ),
        dcc.Graph(id="expression-plot", figure=fig),
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

    for i, isoform in enumerate(matching_isoforms):
        first_of_type = True
        for _, cols in groups_by_type.items():
            x_values = []
            y_values = []
            error_values = []

            for group in cols:
                x_values.append(x_positions_map[group])
                y_values.append(expression_data.loc[(isoform, "mean"), group])
                error_values.append(expression_data.loc[(isoform, "std"), group])

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
                showlegend=first_of_type
            ))
            first_of_type = False

    fig.update_layout(
        title=f'Expression Profile: {selected_gene}',
        yaxis_title="mean/SD TPM",
        height=500,
        showlegend=True,
        xaxis=dict(
            tickvals=[x_positions_map[s] for s in sample_groups],
            ticktext=sample_groups,
            tickangle=45
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.01
        )
    )

    return fig


def _get_x_positions(groups_by_type):
    x_positions_map = {}
    current_pos = 0
    inner_spacing = 0.5
    group_spacing = 1
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


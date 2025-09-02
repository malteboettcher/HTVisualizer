import pandas as pd
from dash import dcc, html

from .data_loader import load_annotation_data, load_quant_data


def create_layout(annotation_path, expression_path):
    annotation_data = load_annotation_data(annotation_path)
    expression_data = load_quant_data(expression_path)
    # fig = px.bar(expression_data)

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
        dcc.Graph(id="expression-plot"),
    ])
    return layout

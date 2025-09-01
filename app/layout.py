import plotly.express as px
from dash import dcc, html

from .data_loader import load_expression_data


def create_layout():
    df = load_expression_data("data/example_data.csv")
    fig = px.bar(df, x="gene", y="expression", title="Expression Values")

    layout = html.Div(children=[
        html.H1("High-Throughput Expression Dashboard"),
        dcc.Graph(id="expression-plot", figure=fig),
        dcc.Dropdown(
            id="gene-selector",
            options=[{"label": g, "value": g} for g in df["gene"].unique()],
            multi=True,
            placeholder="Select genes..."
        ),
    ])
    return layout

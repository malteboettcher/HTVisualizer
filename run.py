import argparse

import dash_bootstrap_components as dbc
from dash import Dash

from app.layout import create_layout


def main(annotation_path, expression_path, host="127.0.0.1", port=8050, debug=True):
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = create_layout(annotation_path, expression_path)
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Dash gene expression app")
    parser.add_argument("--annotation", default="example_data/example_annotation.csv",
                        help="Path to annotation CSV")
    parser.add_argument("--expression", default="example_data/example_quant/",
                        help="Path to expression data folder")
    parser.add_argument("--host", default="127.0.0.1", help="Host to run app on")
    parser.add_argument("--port", type=int, default=8050, help="Port to run app on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()
    main(args.annotation, args.expression, args.host, args.port, args.debug)

from dash import Dash

from app.layout import create_layout

app = Dash(__name__)
app.layout = create_layout("data/Thalemine_gene_names.csv", "data/AtRTD3/")

if __name__ == "__main__":
    app.run(debug=True)

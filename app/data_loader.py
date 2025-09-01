import pandas as pd


def load_expression_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    required_cols = {"gene", "expression"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_cols}")
    return df

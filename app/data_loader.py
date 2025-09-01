import pandas as pd


def load_annotation_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, delimiter=';')
    required_cols = {"AGI", "Name"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_cols}")
    return df

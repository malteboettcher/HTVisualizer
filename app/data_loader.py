from pathlib import Path

import pandas as pd


def load_annotation_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, delimiter=';')
    required_cols = {"AGI", "Name"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_cols}")
    return df


def load_quant_data(filepath: str) -> pd.DataFrame:
    df = pd.DataFrame()

    path = Path(filepath)
    for directory in path.iterdir():
        quant_file = directory / "quant.sf"
        quant_df = pd.read_csv(quant_file, sep="\t")

        quant_df = quant_df[["Name", "TPM"]].set_index("Name")

        quant_df.rename(columns={"TPM": directory.name}, inplace=True)

        df = pd.concat([df, quant_df], axis=1)

    agg_df = df.T.groupby(lambda x: "_".join(x.split("_")[:-1])).agg(['mean', 'std']).T
    return agg_df

from pathlib import Path
from typing import Optional

import pandas as pd


class ExpressionDataManager:
    _instance: Optional['ExpressionDataManager'] = None
    _expression_data: Optional[pd.DataFrame] = None
    _annotation_data: Optional[pd.DataFrame] = None

    _annotation_path: Optional[str] = None
    _quant_path: Optional[str] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,
                 annotation_path: Optional[str] = None,
                 quant_path: Optional[str] = None):
        if self._annotation_path is None and annotation_path is not None:
            self._annotation_path = annotation_path
        if self._quant_path is None and quant_path is not None:
            self._quant_path = quant_path

    def load_annotation_data(self) -> pd.DataFrame:
        if self._annotation_path is None:
            raise ValueError("Path to annotation data is not set.")

        if self._annotation_data is None:
            df = pd.read_csv(self._annotation_path, delimiter=';')
            required_cols = {"AGI", "Name"}
            if not required_cols.issubset(df.columns):
                raise ValueError(f"CSV must contain columns: {required_cols}")
            self._annotation_data = df

        return self._annotation_data


    def load_quant_data(self) -> pd.DataFrame:
        if self._quant_path is None:
            raise ValueError("Path to quantification data is not set.")

        if self._expression_data is None:

            dfs = []
            path = Path(self._quant_path)
            for directory in path.iterdir():
                quant_file = directory / "quant.sf"
                quant_df = pd.read_csv(quant_file, sep="\t")

                quant_df = quant_df[["Name", "TPM"]].set_index("Name")

                quant_df.rename(columns={"TPM": directory.name}, inplace=True)
                dfs.append(quant_df)

            df = pd.concat(dfs, axis=1)

            df = df.loc[~df.index.str.contains("-") & df.index.str.startswith("A")]

            gene_index = df.index.to_series().str.split(r"[.]", n=1).str[0]

            gene_df = df.groupby(gene_index).sum()
            expanded_df = pd.concat([df, gene_df])

            sample_groups = [c.rsplit("_", 1)[0] for c in expanded_df.columns]

            grouper = pd.Series(sample_groups, index=expanded_df.columns)

            expanded_df = (expanded_df.T
                                     .groupby(grouper)
                                     .agg(['mean', 'std'])
                                     .T)
            self._expression_data = expanded_df

        return self._expression_data


    def get_isoforms_for_gene(self, gene_name: str) -> list:
        if self._expression_data is None:
            return []

        matching_isoforms = []
        for index in self._expression_data.index:
            if index[1] == 'mean' and index[0].startswith(f"{gene_name}"):
                matching_isoforms.append(index[0])
        return matching_isoforms

    def get_sample_groups(self) -> list:
        return self._expression_data.columns

    def get_groups_by_genotype(self) -> dict:
        groups_by_type = {}
        for col in self.get_sample_groups():
            genotype = col.split("_")[0]
            if genotype not in groups_by_type:
                groups_by_type[genotype] = []
            groups_by_type[genotype].append(col)
        return groups_by_type


    @property
    def expression_data(self) -> Optional[pd.DataFrame]:
        return self._expression_data

    @property
    def annotation_data(self) -> Optional[pd.DataFrame]:
        return self._annotation_data

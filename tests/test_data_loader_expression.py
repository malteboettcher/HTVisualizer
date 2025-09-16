import math

import numpy as np
import pytest

from app.data_loader import ExpressionDataManager

folders = {
    "1ko_LL18": [
        {"TPM": 0.315105, "AGI": "AT1G01010.1"},
        {"TPM": 0.415105, "AGI": "AT1G01010.1"},
        {"TPM": 0.515105, "AGI": "AT1G01010.1"}
    ],
    "1ko_LL24": [
        {"TPM": 1.234567,"AGI": "AT1G01010.1"},
        {"TPM": 2.234567,"AGI": "AT1G01010.1"}
    ],
    "1ox_LL18": [{"TPM": 2.345678,"AGI": "AT1G01010.1"}],
    "1ox_LL24": [{"TPM": 0.987654,"AGI": "AT1G01010.1"}],
}

@pytest.fixture
def temp_folder_with_structure(tmp_path):
    for folder_name, samples in folders.items():
        for i, data in enumerate(samples, start=1):
            folder = tmp_path / f"{folder_name}_{i}"
            folder.mkdir()
            content = (
                "Name\tLength\tEffectiveLength\tTPM\tNumReads\n"
                f"{data['AGI']}\t1749\t1430.305\t{data['TPM']}\t24"
            )
            if f"{folder_name}_1" == "1ox_LL24_1":
                content += f"\nAT1G01010.2\t1749\t1430.305\t{data['TPM']}\t24\n"
                content += f"\nAT1G01010-AT1G01020.1\t1749\t1430.305\t{data['TPM']}\t24"
            (folder / "quant.sf").write_text(content)

    return tmp_path

@pytest.fixture(autouse=True)
def reset_singleton():
    ExpressionDataManager._instance = None

def test_parse_correct_genotypes_and_ll(temp_folder_with_structure):
    manager = ExpressionDataManager(None, str(temp_folder_with_structure))
    df = manager.load_quant_data()

    for folder_name, _ in folders.items():
        assert folder_name in df.columns


def test_parse_correct_values_for_gene_isoform(temp_folder_with_structure):
    manager = ExpressionDataManager(None, str(temp_folder_with_structure))
    df = manager.load_quant_data()

    for sample_name, samples in folders.items():
        tpms = [sample["TPM"] for sample in samples]
        avg_tpm = sum(tpms) / len(tpms)

        if len(tpms) > 1:
            mean_diff_sq = [(x - avg_tpm) ** 2 for x in tpms]
            std_tpm = math.sqrt(sum(mean_diff_sq) / (len(tpms) - 1))
            assert np.isclose(df.loc[(samples[0]["AGI"], "std"), sample_name], std_tpm,
                              rtol=1e-8, atol=1e-10)

        assert df.loc[(samples[0]["AGI"], "mean"), sample_name] == avg_tpm

def test_get_isoforms_for_gene(temp_folder_with_structure):
    manager = ExpressionDataManager(None, str(temp_folder_with_structure))
    manager.load_quant_data()

    isoforms = manager.get_isoforms_for_gene("AT1G01010")
    assert set(isoforms) == {"AT1G01010", "AT1G01010.1", "AT1G01010.2"}

def test_get_sample_groups(temp_folder_with_structure):
    manager = ExpressionDataManager(None, str(temp_folder_with_structure))
    manager.load_quant_data()
    sample_groups = manager.get_sample_groups()

    assert set(sample_groups) == {"1ko_LL18", "1ko_LL24", "1ox_LL18", "1ox_LL24"}


def test_get_groups_by_genotype(temp_folder_with_structure):
    manager = ExpressionDataManager(None, str(temp_folder_with_structure))
    manager.load_quant_data()
    groups_by_type = manager.get_groups_by_genotype()

    expected = {
        "1ko": ["1ko_LL18", "1ko_LL24"],
        "1ox": ["1ox_LL18", "1ox_LL24"]
    }

    assert groups_by_type == expected

def test_gene_isoform_aggregation_row_added(temp_folder_with_structure):
    manager = ExpressionDataManager(None, str(temp_folder_with_structure))
    df = manager.load_quant_data()

    gene_id = "AT1G01010"

    isoform_names = manager.get_isoforms_for_gene(gene_id)

    assert "AT1G01010.1" in isoform_names, "Individual isoform AT1G01010.1 not found"
    assert "AT1G01010.2" in isoform_names, "Individual isoform AT1G01010.2 not found"

    sample_with_multiple_isoforms = "1ox_LL24"

    if sample_with_multiple_isoforms in df.columns:

        gene_mean = df.loc[(gene_id, "mean"), sample_with_multiple_isoforms]

        isoform1_mean = df.loc[("AT1G01010.1", "mean"), sample_with_multiple_isoforms]
        isoform2_mean = df.loc[("AT1G01010.2", "mean"), sample_with_multiple_isoforms]

        expected_gene_total = isoform1_mean + isoform2_mean
        assert np.isclose(gene_mean, expected_gene_total, rtol=1e-8, atol=1e-10), \
            (f"Gene-level aggregation incorrect: expected "
             f"{expected_gene_total}, got {gene_mean}")

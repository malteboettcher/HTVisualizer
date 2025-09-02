import math

import numpy as np
import pytest

from app.data_loader import load_quant_data

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
            if folder_name == "1ox_LL24_1":
                content += f"\nAT1G01010.2\t1749\t1430.305\t{data['TPM']}\t24"
            (folder / "quant.sf").write_text(content)

    return tmp_path



def test_parse_correct_genotypes_and_ll(temp_folder_with_structure):
    df = load_quant_data(str(temp_folder_with_structure))

    for folder_name, _ in folders.items():
        assert folder_name in df.columns


def test_parse_correct_values_for_gene_isoform(temp_folder_with_structure):
    df = load_quant_data(str(temp_folder_with_structure))

    for sample_name, samples in folders.items():
        tpms = [sample["TPM"] for sample in samples]
        avg_tpm = sum(tpms) / len(tpms)

        if len(tpms) > 1:
            mean_diff_sq = [(x - avg_tpm) ** 2 for x in tpms]
            std_tpm = math.sqrt(sum(mean_diff_sq) / (len(tpms) - 1))
            assert np.isclose(df.loc[(samples[0]["AGI"], "std"), sample_name], std_tpm,
                              rtol=1e-8, atol=1e-10)

        assert df.loc[(samples[0]["AGI"], "mean"), sample_name] == avg_tpm


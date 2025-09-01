import pytest

from app.data_loader import load_quant_data

folders = {
    "1ko_LL18": {"TPM": 0.315105, "AGI": "AT1G01010.1"},
    "1ko_LL24": {"TPM": 1.234567, "AGI": "AT1G01010.1"},
    "1ox_LL18": {"TPM": 2.345678, "AGI": "AT1G01010.1"},
    "1ox_LL24": {"TPM": 0.987654, "AGI": "AT1G01010.1"},
}

@pytest.fixture
def temp_folder_with_structure(tmp_path):
    for folder_name, data in folders.items():
        folder = tmp_path / folder_name
        folder.mkdir()
        content = (
            "Name\tLength\tEffectiveLength\tTPM\tNumReads\n"
            f"{data['AGI']}\t1749\t1430.305\t{data['TPM']}\t24"
        )
        if folder_name == "1ox_LL24":
            content += f"\nAT1G01010.2\t1749\t1430.305\t{data['TPM']}\t24"
        (folder / "quant.sf").write_text(content)

    return tmp_path



def test_parse_correct_genotypes_and_ll(temp_folder_with_structure):
    df = load_quant_data(str(temp_folder_with_structure))

    for folder_name, _ in folders.items():
        assert folder_name in df.columns


def test_parse_correct_values_for_gene_isoform(temp_folder_with_structure):
    df = load_quant_data(str(temp_folder_with_structure))

    for folder_name, data in folders.items():
        assert df.loc[data['AGI'], folder_name] == data["TPM"]


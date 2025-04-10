import pytest
import pandas as pd
from create_spreadsheets import find_sheet_with_id, create_empty_dataframes, append_to_csv, process_data

@pytest.fixture
def setup_variables():
    try:
        size_name, metadata_name, sample_name, global_path = create_empty_dataframes("test_id")
        return [size_name, metadata_name, sample_name, global_path]
    except Exception as e:
        pytest.fail(f"Setup failed: {e}")

def test_find_sheet_with_id():
    assert find_sheet_with_id("Nanopore Run 000.xlsx", "test_id") == "Test Run 000"
    assert find_sheet_with_id("Nanopore Run 000.xlsx", "test_id_nb") == "Test Run 001"

def test_create_empty_dataframes():
    size_name, metadata_name, sample_name, global_path = create_empty_dataframes("test_id")
    assert size_name == "test_id_size_sheet.csv"
    assert metadata_name == "test_id_metadata.txt"
    assert sample_name == "test_id_sample.txt"
    assert global_path == "/global/home/groups/fc_fpsdnaseq/test_id"

    # read the csvs and check them
    with open("test_id_size_sheet.csv", "r") as file:
        content = file.read()
        assert content == "barcode,alias,approx_size\n"

    with open("test_id_metadata.txt", "r") as file:
        content = file.read()
        assert content == "sequencing_set_path,plate,barcode_num,reference_path\n"

    with open("test_id_sample.txt", "r") as file:
        content = file.read()
        assert content == "name,plate,barcode_num,return_type,sample\n"

def test_append_to_csv():
    df = pd.DataFrame(columns=['Column1'])
    df.to_csv("test.csv", index=False)
    df2 = pd.DataFrame([{'Column1': 'test_value'}])
    append_to_csv(df2, "test.csv")
    with open("test.csv", "r") as file:
        content = file.read()
        assert content == "Column1\ntest_value\n"

def test_process_data(setup_variables):
    size_name, metadata_name, sample_name, global_path = setup_variables
    data = pd.read_excel(
        "Nanopore Run 000.xlsx",
        sheet_name="Test Run 000",
        usecols='B,C,D,G,H,I',
        skiprows=1,
        skipfooter=2
    )
    data.columns = ['customer_name', 'sample_name', 'barcode', 'size', 'reference_name', 'sample_type']
    process_data(data, global_path, size_name, metadata_name, sample_name)

    for file in [size_name, metadata_name]:
        with open(file, "r") as actual, open(f"expected_outputs/{file}", "r") as expected:
            assert actual.read() == expected.read(), f"Mismatch in file: {file}"

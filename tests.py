import unittest
import pandas as pd

from create_spreadsheets import find_sheet_with_id, create_empty_dataframes, append_to_csv, process_data

class TestCreateSpreadsheet(unittest.TestCase):

    def setUp(self):
        # Attempt to create dataframes in setup and store state
        # note that these depend on create_empty_dataframes, which is not tested here
        self.variables_initialized = False
        try:
            size_name, metadata_name, sample_name, global_path = create_empty_dataframes("test_id")
            self.variables = [size_name, metadata_name, sample_name, global_path]
            self.size_name = size_name
            self.metadata_name = metadata_name
            self.sample_name = sample_name
            self.global_path = global_path
            self.variables_initialized = True
        except Exception as e:
            print(f"Setup failed: {e}")

    def test_find_sheet_with_id(self):
        self.assertEqual(find_sheet_with_id("Nanopore Run 000.xlsx", "test_id"), "Test Run 000")
        self.assertEqual(find_sheet_with_id("Nanopore Run 000.xlsx", "test_id_nb"), "Test Run 001")

    def test_create_empty_dataframes(self):
        size_name, metadata_name, sample_name, global_path = create_empty_dataframes("test_id")
        self.assertEqual(size_name, "test_id_size_sheet.csv")
        self.assertEqual(metadata_name, "test_id_metadata.txt")
        self.assertEqual(sample_name, "test_id_sample.txt")
        self.assertEqual(global_path, "/global/home/groups/fc_fpsdnaseq/test_id")

        # read the csvs and check them:
        with open("test_id_size_sheet.csv", "r") as file:
            content = file.read()
            self.assertEqual(content, "barcode,alias,approx_size\n")

        with open("test_id_metadata.txt", "r") as file:
            content = file.read()
            self.assertEqual(content, "sequencing_set_path,plate,barcode_num,reference_path\n")

        with open("test_id_sample.txt", "r") as file:
            content = file.read()
            self.assertEqual(content, "name,plate,barcode_num,return_type,sample\n")

    def test_append_to_csv(self):
        df = pd.DataFrame(columns=['Column1'])
        df.to_csv("test.csv", index=False)
        df2 = pd.DataFrame([{'Column1': 'test_value'}])
        append_to_csv(df2, "test.csv")
        with open("test.csv", "r") as file:
            content = file.read()
            self.assertEqual(content, "Column1\ntest_value\n")

    def test_process_data(self):
        data = pd.read_excel("Nanopore Run 000.xlsx", sheet_name="Test Run 000", usecols='B,C,D,G,H,I', skiprows=1, skipfooter=2)
        data.columns = ['customer_name', 'sample_name', 'barcode', 'size', 'reference_name', 'sample_type']
        process_data(data, self.variables[3], self.variables[0], self.variables[1], self.variables[2])

        for file in self.variables[0:2]: 
            with open(file, "r") as actual, open(f"expected_outputs/{file}", "r") as expected:
                self.assertEqual(actual.read(), expected.read(), f"Mismatch in file: {file}")

if __name__ == '__main__':
    unittest.main()
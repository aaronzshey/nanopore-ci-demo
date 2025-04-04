# edited march 20th, 2025  by Aaron Shey
# Fixed an error where if the sheet containing 20250228NB preceded
# the sheet containing 20250228, searching for 20250228 would return
# the wrong sheet 

import pandas as pd
import numpy as np
import sys
import glob

def find_sheet_with_id(excel_file, search_id):
    # Load the entire Excel file into a dictionary of DataFrames
    xlsx_dict = pd.read_excel(excel_file, sheet_name=None, usecols='C', nrows=1)

    # Iterate through each DataFrame in the dictionary and search for the string
    for sheet_name, df in xlsx_dict.items():
        # print(f"checking sheet {sheet_name}")
        if search_id in df.to_string().split():
            return sheet_name
        
    return None

def create_empty_dataframes(run_id):
    # Names for files 
    SIZE_FILE_NAME_ROOT = '_size_sheet.csv'
    METADATA_FILE_NAME_ROOT = '_metadata.txt'
    SAMPLE_FILE_NAME_ROOT = '_sample.txt'
    GLOBAL_PATH_PREFIX = '/global/home/groups/fc_fpsdnaseq/'

    # Build the file and path names
    size_name = run_id + SIZE_FILE_NAME_ROOT
    metadata_name = run_id + METADATA_FILE_NAME_ROOT
    sample_name = run_id + SAMPLE_FILE_NAME_ROOT

    # Create DataFrames for each set of columns
    size_df = pd.DataFrame(columns=['barcode', 'alias', 'approx_size'])
    metadata_df = pd.DataFrame(columns=['sequencing_set_path', 'plate', 'barcode_num', 'reference_path'])
    sample_df = pd.DataFrame(columns=['name', 'plate', 'barcode_num', 'return_type', 'sample'])

    # Write the DataFrames to CSV files
    size_df.to_csv(size_name, index=False, header=True)
    metadata_df.to_csv(metadata_name, index=False, header=True)
    sample_df.to_csv(sample_name, index=False, header=True)

    return size_name, metadata_name, sample_name, GLOBAL_PATH_PREFIX + run_id

def append_to_csv(df, file_name):
    df.to_csv(file_name, mode='a', header=False, index=False)

def process_data(data, global_path, size_name, metadata_name, sample_name):
    for _index, row in data.iterrows():
        # Add the leading zero
        barcode_num_padded = "barcode" + str(row['barcode']).zfill(2)

        # Build size
        size_df = pd.DataFrame([{
            'barcode': barcode_num_padded,
            'alias': barcode_num_padded,
            'approx_size': 7000 if pd.isna(row['size']) else row['size']
        }])
        append_to_csv(size_df, size_name)

        # Build metadata
        metadata_df = pd.DataFrame([{
            'sequencing_set_path': global_path,
            'plate': 'plate1',
            'barcode_num': barcode_num_padded,
            'reference_path': global_path + '/reference_fastas/' + barcode_num_padded + '.final.fasta'
        }])
        append_to_csv(metadata_df, metadata_name)

        # need to refactor this to use map and a function instead of a loop
        if pd.notna(row['reference_name']):
            # constant
            reference_names = row['reference_name'].split("_UNIQUE_STRING_")
            for name in reference_names:
                metadata_df = pd.DataFrame([{
                    'sequencing_set_path': global_path,
                    'plate': 'plate1',
                    'barcode_num': barcode_num_padded,
                    'reference_path': global_path + '/reference_fastas/' + name + '.fasta'
                }])   
                append_to_csv(metadata_df, metadata_name)       

        # Build sample
        sample_df = pd.DataFrame([{
            'name': row['customer_name'],
            'plate': 'plate1',
            'barcode_num': barcode_num_padded,
            'return_type': row['sample_type'],
            'sample': row['sample_name']
        }])
        append_to_csv(sample_df, sample_name)

def main(run_id):
    matching_files = glob.glob("Nanopore Run *.xlsx")

    if matching_files:
        # Select the first match
        excel_file_name = matching_files[0]
        print(f"Selected file: {excel_file_name}")
    else:
        print("No matching files found.")
        sys.exit()


    # Create empty DataFrames
    size_name, metadata_name, sample_name, global_path = create_empty_dataframes(run_id)

    # Find the correct sheet from the run ID
    found_sheet = find_sheet_with_id(excel_file_name, run_id)

    if found_sheet:
        print(f"String '{run_id}' found in sheet: {found_sheet}")
    else:
        print(f"String '{run_id}' not found in any sheet. Make sure it's in the spreadsheet.")
        sys.exit()

    # Load the data from the found sheet
    data = pd.read_excel(excel_file_name, sheet_name=found_sheet, usecols='B,C,D,G,H,I', skiprows=1, skipfooter=2)
    data.columns = ['customer_name', 'sample_name', 'barcode', 'size', 'reference_name', 'sample_type']

    # Process the data
    process_data(data, global_path, size_name, metadata_name, sample_name)

if __name__ == "__main__":
    run_id = sys.argv[1]

    if not run_id:
        print("Please provide a run ID.")
        sys.exit()
        
    main(run_id)

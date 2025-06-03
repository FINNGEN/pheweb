import os
import argparse
import gzip
import re

def generate_column_group(key, output_header):
    """
    generate resulted row after using dict mapping
    """
    print(key, output_header)
    return f"generate_column_group"

def run(input_file, output_file):

    # write the array of objects to a csv file
    if os.path.exists(output_file):
        os.remove(output_file)  # Overwrite the file with an empty DataFrame
        print(f"File '{output_file}' is already exist, so it is cleared first to remove the old contents")

    # read in the files
    try:
        # Read the first line (header)
        with gzip.open(input_file, 'rt') as f:
            header = f.readline().strip().split('\t')
            # print("Header columns:", header)
            final_header_list = []
            for column in header:
                pattern = re.compile(fr'^{column}_')
                matching_columns = [col for col in header if pattern.match(col)]
                if (len(matching_columns) > 0):
                    header_list = []
                    header_list.append(header[0])
                    header_list.append(column)
                    header_list.extend(matching_columns)
                    final_header_list.append(header_list)
                    print('.', end='', flush=True)
            # print(final_header_list)
            for line in f:
                row = line.strip().split('\t')  # split by tab to get columns
                print(row)

    except Exception as e:  # Catch any exception
        print(f"An error occurred: {e}")
        raise

# check the argument 
parser = argparse.ArgumentParser(description="Convert the long format into short format!")
parser.add_argument('input_file_path', type=str)
parser.add_argument('output_file_name', type=str)

args = parser.parse_args()

if f"/{args.input_file_path}".endswith('.tsv.gz'):
    run(args.input_file_path, args.output_file_name)
else:
    print("Sorry, output file name should be tsv.gx. e-g string.tsv.gz")
    exit(1)

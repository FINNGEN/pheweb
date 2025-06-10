import re
import sys
import argparse
import gzip

FINNGENID = 'FINNGENID'
COLUMN = 'COLUMN';
VALUE = 'VALUE';

def print_progress_bar(iteration, total, prefix='', suffix='', length=50):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        print()  # Newline at the end

def run(input_file, output_file, output_suffix_columns):
    try:
        matched_header = '_' + output_suffix_columns.replace('|','|_')
        pattern = re.compile(fr'{matched_header}')
        sufficies = matched_header.split('|')
        provided_columns = output_suffix_columns.replace("|", "\t")
        start = 1
        end = 100
        # Read the entire TSV gzip file into a
        with gzip.open(output_file,"wt",encoding="utf-8") as output:
            with gzip.open(input_file, 'rt') as file:
                # read the header line             
                header_line = file.readline().strip().split('\t')
                header_dict = {name: idx for idx, name in enumerate(header_line)}
                # Filter out matching keys and FINNGENID
                filtered_header_data = {k: v for k, v in header_dict.items() if not pattern.search(k) and k != FINNGENID}
                output_file_header = f"{FINNGENID}\t{COLUMN}\t{VALUE}\t{provided_columns}\n"
                output.write(output_file_header)
                for index, line in enumerate(file, start=0):
                    row = line.strip().split('\t')                    
                    for key, value in filtered_header_data.items():
                        resulted_row = []
                        resulted_row.append(row[header_dict[FINNGENID]])
                        resulted_row.append(key)
                        resulted_row.append(row[value])
                        for suffix in sufficies:
                            prefix_column = f"{key}{suffix}"
                            resulted_row.append(row[header_dict[prefix_column]])
                        if len(resulted_row) == len(output_file_header.split('\t')):
                            output.write(f'\t'.join(resulted_row)+'\n')
                    # add progress bar start and end run for each 100 rows
                    start = 1 if index % 100 == 0 else start + 1
                    end = 100 if index % 100 == 0 else end
                    progress_bar_suffix = f"first {end}" if index < 100 else f"upto {index + 1}"
                    print_progress_bar(start, end, prefix='Progress', suffix=progress_bar_suffix, length=40)
        print('\nFinished successfully!')
    except Exception as e:  # Catch any exception
        print(f"An error occurred: {e}")
        raise

# check the argument 
parser = argparse.ArgumentParser(description="Convert the wide format into long format!")
parser.add_argument('input_file_path', type=str, help="The input file in gx wide format e-g: path/to/input.tsv.gz")
parser.add_argument('output_file_name', type=str, help="The output file in gx format e-g: path/to/output.tsv.gz")
parser.add_argument('filter_columns', type=str, help="The list of suffixes e-g: SUFFIX1|SUFFIX2|SUFFIX3")

args = parser.parse_args()

run(args.input_file_path, args.output_file_name, args.filter_columns)

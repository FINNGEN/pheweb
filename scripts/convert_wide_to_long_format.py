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


def run(input_file, output_file, columns):
    try:
        with gzip.open(output_file,"wt",encoding="utf-8") as output:
            # Read the first line (header)
            print('start reading rows')
            with gzip.open(input_file, 'rt') as file:
                header_line = file.readline().strip().split('\t')
                provided_columns = columns.replace("|", "\t")
                output_file_header = f"{FINNGENID}\t{COLUMN}\t{VALUE}\t{provided_columns}\n"
                output.write(output_file_header)
                sufficies = columns.split('|')
                # reading input file line
                for line in file:
                    row = line.strip().split('\t')
                    for header_key in header_line:
                        resulted_row = []
                        if header_line.index(header_key) == 0:
                            finn_gen_id = row[header_line.index(header_key)]
                            continue
                        else:
                            resulted_row.append(finn_gen_id)
                            resulted_row.append(f"{header_key}")
                            resulted_row.append(row[header_line.index(header_key)])
                            for suffix in sufficies:
                                prefix_column = f"{header_key}_{suffix}"
                                if prefix_column in header_line:
                                    resulted_row.append(row[header_line.index(prefix_column)])
                        if (len(resulted_row) == len(output_file_header.split('\t'))):
                           output.write(f"\t".join(resulted_row)+"\n")
                        print_progress_bar(header_line.index(header_key), len(header_line) + 1, prefix='Progress', suffix=f"FINNGENID {row[0]} Complete", length=40)
        print('\nFinished successfully!')
    except Exception as e:  # Catch any exception
        print(f"An error occurred: {e}")
        raise

# check the argument 
parser = argparse.ArgumentParser(description="Convert the wide format into long format!")
parser.add_argument('input_file_path', type=str)
parser.add_argument('output_file_name', type=str)
parser.add_argument('filter_columns', type=str)

args = parser.parse_args()

run(args.input_file_path, args.output_file_name, args.filter_columns)

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
                header = file.readline().strip().split('\t')
                provided_columns = columns.replace("|", "\t")
                output_file_header = f"{FINNGENID}\t{COLUMN}\t{VALUE}\t{provided_columns}\n"
                output.write(output_file_header)
                sufficies = columns.split('|')
                # reading input file line
                for line in file:
                    row = line.strip().split('\t')
                    for head in header:
                        resulted_row = []
                        if header.index(head) == 0:
                            finn_gen_id = row[header.index(head)]
                            continue
                        else:
                            resulted_row.append(finn_gen_id)
                            resulted_row.append(f"{head}")
                            resulted_row.append(row[header.index(head)])
                            for suffix in sufficies:
                                prefix_column = f"{head}_{suffix}"
                                if prefix_column in header:
                                    resulted_row.append(row[header.index(prefix_column)])
                        if (len(resulted_row) == len(output_file_header.split('\t'))):
                           output.write(f"\t".join(resulted_row)+"\n")
                        print_progress_bar(header.index(head), len(header) + 1, prefix='Progress', suffix=f"FINNGENID {row[0]} Complete", length=40)
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

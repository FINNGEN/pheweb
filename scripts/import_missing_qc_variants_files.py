import os
import csv
import argparse

def get_files_list(input_path, output_path):
    files = []
    for filename in os.listdir(input_path):
        file_path = os.path.join(input_path, filename)
        if output_path not in file_path and file_path.endswith('.tsv'):
            files.append(file_path)
    return files

def generate_resulted_row(custom_header, row):
    resulted_row = []
    variant = row[custom_header.index('Variant')]
    splited_variant = variant.split(":")
    resulted_row.insert(0, splited_variant[0].replace('chr', ''))
    resulted_row.insert(1, splited_variant[1])
    resulted_row.insert(2, variant.replace('chr', ''))
    resulted_row.insert(3, row[custom_header.index('variant_qc.call_rate')])
    resulted_row.insert(5, row[custom_header.index('variant_qc.AF')])
    resulted_row.insert(6, row[custom_header.index('variant_qc.n_called')])
    resulted_row.insert(7, row[custom_header.index('variant_qc.n_not_called')])
    resulted_row.insert(8, 'NA')
    resulted_row.insert(9, row[custom_header.index('variant_qc.n_het')])
    resulted_row.insert(10, 'NA')
    resulted_row.insert(11, row[custom_header.index('variant_qc.dp_stats.mean')])
    resulted_row.insert(12, row[custom_header.index('variant_qc.dp_stats.stdev')])
    resulted_row.insert(13, row[custom_header.index('variant_qc.gq_stats.mean')])
    resulted_row.insert(14, row[custom_header.index('variant_qc.gq_stats.stdev')])
    resulted_row.insert(15, row[custom_header.index('variant_qc.n_non_ref')])
    resulted_row.insert(16, 'NA')
    resulted_row.insert(17, 'NA')
    resulted_row.insert(18, 'NA')
    resulted_row.insert(19, row[custom_header.index('variant_qc.p_value_hwe')])
    resulted_row.insert(20, row[custom_header.index('filters')])
    resulted_row.insert(21, row[custom_header.index('info.QD')])
    resulted_row.insert(22, 'NA')
    resulted_row.insert(23, 'NA')
    resulted_row.insert(24, row[custom_header.index('IS_LCR')])
    resulted_row.insert(25, row[custom_header.index('failed_filter')])
    return f"\t".join(resulted_row)+"\n"

def main_script(input_path, output_path):
    filenames = get_files_list(input_path, output_path)
    filenames.sort()

    # write the array of objects to a csv file
    if os.path.exists(output_path):
        os.remove(output_path)  # Overwrite the file with an empty DataFrame
        print(f"File '{output_path}' is already exist, so it is cleared first to remove the old contents")

    # read in the files
    with open(output_path,"wt",encoding="utf-8") as out_file:
        try:
            # flag to check header is written or not
            is_header_written = False
            for fname in filenames:
                with open(fname,"rt",encoding="utf-8") as infile:
                    print(fname)
                    print('Loading data ...')
                    reader = csv.reader(infile, delimiter='\t')
                    custom_header = []
                    for row in reader:
                        if len(row) == 24:
                            # check if header is not present in output file
                            if 'Variant' in row and row.index('Variant') < 1 and is_header_written is False:
                                row.insert(0, '#chrom')
                                row.insert(1, 'pos')
                                final_header = "\t".join(row)+"\n"
                                out_file.write(final_header)
                                is_header_written = True
                            elif 'Variant' in row and is_header_written is True:
                                continue
                            else:
                                splited_variant = row[0].split(":")
                                row.insert(0, splited_variant[0])
                                row.insert(1, splited_variant[1])
                                line = f"\t".join(row)+"\n"
                                out_file.write(line)
                        elif len(row) > 24:
                            if 'Variant' in row and row.index('Variant') > 0:
                                custom_header = row
                                continue
                            else:
                                line = generate_resulted_row(custom_header, row)
                                out_file.write(line)
                        else:
                            print(f"Sorry! The file {fname} and {row} does not consist on proper tsv columns.")
                            exit(1)
                print(f"Finished!")
        except Exception as e:  # Catch any exception
            print(f"An error occurred: {e}")

# check the argument 
parser = argparse.ArgumentParser(description="The QC variant import script!")

parser.add_argument('input_file_path', type=str, default='/mnt/disks/data/data-directory/path/to/qc_variant_folder')
parser.add_argument('output_file_name', type=str, default='combined_sorted_output_file.tsv')

args = parser.parse_args()

if args.input_file_path and args.output_file_name:
    INPUT_FOLDER_PATH = args.input_file_path
    if f"/{args.output_file_name}".endswith('.tsv'):
        OUTPUT_FOLDER_PATH = INPUT_FOLDER_PATH + f"/{args.output_file_name}"
        main_script(INPUT_FOLDER_PATH, OUTPUT_FOLDER_PATH)
    else:
        print("Sorry, output file name should be tsv. e-g string.tsv")
        exit(1)
else:
    print("Sorry, qc variants folder path or output tsv file name is missing!")
    exit(1)

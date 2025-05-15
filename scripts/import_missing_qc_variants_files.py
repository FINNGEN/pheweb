import os, sys
import csv
import argparse

def get_files_list(input_path, output_path):
    files = []
    for filename in os.listdir(input_path):
        file_path = os.path.join(input_path, filename)
        if output_path not in file_path and file_path.endswith('.tsv'):
            files.append(file_path)
    return files

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
            # output file header
            output_file_reader = csv.reader(out_file)
            is_header_written = False
            # store the header for output file
            output_file_header = next(output_file_reader) if not os.path.getsize(output_path) == 0 else None
            for fname in filenames:
                with open(fname,"rt",encoding="utf-8") as infile:
                    print(fname)
                    print('Loading data ...')
                    reader = csv.reader(infile, delimiter='\t')
                    for row in reader:
                        if len(row) == 24:
                            # check if header is not present in output file
                            if row[0] == 'Variant' and is_header_written is False and output_file_header is None:
                                row.insert(0, '#chrom')
                                row.insert(1, 'pos')
                                final_header = "\t".join(row)+"\n"
                                out_file.write(final_header)
                                is_header_written = True
                            elif row[0] == 'Variant' and is_header_written is True and output_file_header is None:
                                continue
                            else:
                                splited_variant = row[0].split(":")
                                row.insert(0, splited_variant[0])
                                row.insert(1, splited_variant[1])
                                line = f"\t".join(row)+"\n"
                                out_file.write(line)
                        elif len(row) == 29:
                            if (row[25] == 'Variant'):
                                continue
                            else:
                                new_row = []
                                splited_variant = row[25].split(":")
                                new_row.insert(0, splited_variant[0])
                                new_row.insert(1, splited_variant[1])
                                new_row.insert(2, row[25])
                                new_row.insert(3, row[15])
                                new_row.insert(4, row[11])
                                new_row.insert(5, row[12])
                                new_row.insert(6, row[16])
                                new_row.insert(7, row[17])
                                new_row.insert(8, 'NA')
                                new_row.insert(9, row[19])
                                new_row.insert(10, 'NA')
                                new_row.insert(11, row[3])
                                new_row.insert(12, row[4])
                                new_row.insert(13, row[7])
                                new_row.insert(14, row[8])
                                new_row.insert(15, row[20])
                                new_row.insert(16, 'NA')
                                new_row.insert(17, 'NA')
                                new_row.insert(18, 'NA')
                                new_row.insert(19, row[22])
                                new_row.insert(20, row[2])
                                new_row.insert(21, row[24])
                                new_row.insert(22, 'NA')
                                new_row.insert(23, 'NA')
                                new_row.insert(24, row[26])
                                new_row.insert(25, row[28])
                                line = f"\t".join(new_row)+"\n"
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

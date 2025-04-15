import os, sys
import csv

def get_files_list(input_path, output_path, skipped_file_path):
    files = []
    for filename in os.listdir(input_path):
        file_path = os.path.join(input_path, filename)
        if output_path not in file_path and skipped_file_path not in file_path and file_path.endswith('.tsv'):
            files.append(file_path)
    return files

def main_script(input_path, output_path, skipped_file_path):
    filenames = get_files_list(input_path, output_path, skipped_file_path)
    filenames.sort()

    # write the array of objects to a csv file
    if os.path.exists(output_path):
        os.remove(output_path)  # Overwrite the file with an empty DataFrame
        print(f"\nFile '{output_path}' is already exist, so it is cleared first to remove the old contents")

    # read in the files
    with open(output_path,"wt",encoding="utf-8") as out_file:
        try:
            # output file header
            output_file_reader = csv.reader(out_file)
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
                            if row[0] == 'Variant' and output_file_header is None:
                                row.insert(0, '#chrom')
                                row.insert(1, 'pos')
                                final_header = "\t".join(row)+"\n"
                                out_file.write(final_header)
                            else:
                                splited_variant = row[0].split(":")
                                row.insert(0, splited_variant[0])
                                row.insert(1, splited_variant[1])
                                line = f"\t".join(row)+"\n"
                                out_file.write(line)
                        else:
                            print(f"Sorry! The file {fname} and {row} does not consist on proper csv columns.")
                            exit(1)
                print(f"Finished!")
        except Exception as e:  # Catch any exception
            print(f"An error occurred: {e}")

# check the argument 
if len(sys.argv) == 3:
    INPUT_FOLDER_PATH = sys.argv[1]
    if f"/{sys.argv[2]}".endswith('.tsv'):
        OUTPUT_FOLDER_PATH = INPUT_FOLDER_PATH + f"/{sys.argv[2]}"
        SKIPPED_FILE_PATH = 'chrX.removed.add_LCR.add_XPAR.add_failed_filter_awk.tsv'
        main_script(INPUT_FOLDER_PATH, OUTPUT_FOLDER_PATH, SKIPPED_FILE_PATH)
    else:
        print("Sorry, output file name should be tsv. e-g string.tsv")
        exit(1)
else:
    print("Sorry, qc variants folder path or output tsv file name is missing!")
    exit(1)

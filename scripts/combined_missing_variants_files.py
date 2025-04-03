import os
import csv
import gzip

# file constant
folder_path = '/mnt/disks/data/data-directory/variant_qc/panel_variant_qc'
output_fname = folder_path + "/combined_sorted_output_file.tsv.gz"
# Output tsv Gzipped file path
output_gzipped_tsv = output_fname + ".gz"
skipped_file_name = 'chrX.removed.add_LCR.add_XPAR.add_failed_filter_awk.tsv'

# List all files in the folder
def get_files_list():
    files = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if file_path != output_fname and not skipped_file_name in file_path:
            files.append(file_path)
    return files


def main():
    filenames = get_files_list()
    filenames.sort()

    # write the array of objects to a csv file
    if os.path.exists(output_fname):
        os.remove(output_fname)  # Overwrite the file with an empty DataFrame
        print(f"\nFile '{output_fname}' is already exist, so it is cleared first.")

    # read in the files
    with open(output_fname,"wt",encoding="utf-8") as out_file:
        # output file header
        output_file_reader = csv.reader(out_file)
        output_file_header = None
        if not os.path.getsize(output_fname) == 0:
            output_file_header = next(output_file_reader)
            print(output_file_header)
        for fname in filenames:
            with open(fname,"rt",encoding="utf-8") as infile:
                print(fname)
                print('Loading data ...')
                reader = csv.reader(infile, delimiter='\t')
                for row in reader:
                    if len(row) == 24:
                        final_header = "\t".join(row)+"\tchrom\tpos\n"
                        if row[0] == 'Variant' and output_file_header is None:
                                    out_file.write(final_header)
                        else:
                            splited_variant = row[0].split(":")
                            # print(splited_variant)
                            chromosome_value = splited_variant[0]
                            position_value = splited_variant[1]
                            line = "\t".join(row)
                            out_file.write(f"{line.strip()}\t{chromosome_value}\t{position_value}\n")
                    else:
                        print(f"Sorry! The file {fname} does not consist on proper csv columns.")
                        exit(1)
            print(f"Finished!")

main()
import os
import csv
import gzip

# file constant
folder_path = '/mnt/disks/data/data-directory/variant_qc/panel_variant_qc'
output_fname = folder_path + "/combined_sorted_output_file.tsv"
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
                        print(row)
                        print(f"Sorry! The file {fname} does not consist on proper csv columns.")
                        exit(1)
            print(f"Finished!")


    # Open the input TSV file and output .tsv.gz file
    with open(output_fname, mode='r', newline='') as infile, gzip.open(output_gzipped_tsv, mode='wt', newline='') as outfile:
        # Create a TSV reader and writer with tab as the delimiter
        reader = csv.reader(infile, delimiter='\t')
        writer = csv.writer(outfile, delimiter='\t')
        
        # Write each row from the input TSV to the Gzipped output file
        for row in reader:
            print('.', end='', flush=True)
            writer.writerow(row)

    print("TSV file has been compressed to .tsv.gz.")

    # # read in the files
    # for fname in [folder_path + "/chr7.removed.add_LCR.add_failed_filter_awk.tsv"]:
    #     with open(fname,"rt",encoding="utf-8") as infile:
    #         print(fname)
    #         print('Loading data ...')
    #         reader = csv.reader(infile, delimiter='\t')
    #         for row in reader:
    #             if len(row) == 24:
    #                 final_header = "\t".join(row)+"\tchrom\tpos\n"
    #                 if row[0] == 'Variant':
    #                         if final_header not in final_rows:
    #                             final_rows.append(final_header)
    #                 else:
    #                     splited_variant = row[0].split(":")
    #                     # print(splited_variant)
    #                     chromosome_value = splited_variant[0]
    #                     position_value = splited_variant[1]
    #                     line = "\t".join(row)
    #                     resulted_row = f"{line.strip()}\t{chromosome_value}\t{position_value}\n"
    #                     final_rows.append(resulted_row)
    #             else:
    #                 print(f"Sorry! The file {fname} does not consist on proper csv columns.")
    #                 exit(1)
    #     print(f"Finished!")


    # # open the output file
    # with open(output_fname,"wt",encoding="utf-8") as out_file:
    #     # output file header
    #     output_file_reader = csv.reader(out_file)
    #     output_file_header = None
    #     if not os.path.getsize(output_fname) == 0:
    #         output_file_header = next(output_file_reader)
    #         print(output_file_header)
    #     # read in the files
    #     for fname in [folder_path + "/chr7.removed.add_LCR.add_failed_filter_awk.tsv"]:
    #         with open(fname,"rt",encoding="utf-8") as infile:
    #             # read header
    #             reader = csv.reader(infile)
    #             header = next(reader)
    #             # header index is a dictionary that indexes into the correct columns in the file, e.g. if column "AC" is in index 3, then header_index["AC"] = 3 -> we can use it in cols[header_index["AC"]] to get the value of AC for that line. 
    #             header_index = {column_name: index for index, column_name in enumerate(header)}
    #             # print(header_index)
    #             # if we haven't written the header for the output file, write header with new columns chrom and pos
    #             output_header = f"{header[0].strip()}\tchrom\tpos\n"
    #             print(output_header)
    #             #TODO if we haven't writtern the output header, write it to the output
    #             if output_file_header is None:
    #                 prin
    #                 out_file.write(output_header)
    #             #then, for each line, we want to take the line, and from the variant column, separate the chromosome and position values, adding them to the columns
    #             for line in infile:
    #                 cols = line.strip().split("\t")
    #                 #extract the variant column from the columns
    #                 print(cols)
    #                 variant_col = cols[header_index["Variant"]]
    #                 variant_col_split = variant_col.split(":")
    #                 # extract the chromosome and position from the variant column
    #                 chromosome_value = variant_col_split[0]
    #                 position_value = variant_col_split[1]
    #                 # write 
    #                 out_file.write(f"{line.strip()}\t{chromosome_value}\t{position_value}\n")
    
    # write the array of objects to a csv file
    # if os.path.exists(output_fname):
    #     os.remove(output_fname)  # Overwrite the file with an empty DataFrame
    #     print(f"\nFile '{output_fname}' is already exist, so it is cleared first.")
    
    # with open(output_fname,"wt",encoding="utf-8") as out_file:
    #     writer = csv.writer(out_file)
    #     writer.writerows(final_rows)


main()
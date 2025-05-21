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

# mapping the columns name from chrom xfile => autosomal
COLUMNS_MAPPING_DICT = {
    "Variant": "Variant",
    "callRate": "variant_qc.call_rate",
    "AF": "variant_qc.AF",
    "nCalled": "variant_qc.n_called",
    "nNotCalled": "variant_qc.n_not_called",
    "nHet": "variant_qc.n_het",
    "dpMean": "variant_qc.dp_stats.mean",
    "dpStDev": "variant_qc.dp_stats.stdev",
    "gqMean": "variant_qc.gq_stats.mean",
    "gqStDev": "variant_qc.gq_stats.stdev",
    "nNonRef": "variant_qc.n_non_ref",
    "pHWE": "variant_qc.p_value_hwe",
    "FILTERS": "filters",
    "QD": "info.QD",
    "IS_LCR": "IS_LCR",
    "failed_filter": "failed_filter"
}

def generate_resulted_row(output_header, row, xfile_header):
    """
    generate resulted row after using dict mapping
    """
    resulted_row = []
    xfile_columns_index = {}
    
    for index,name in enumerate(xfile_header): 
        xfile_columns_index[name] = index

    variant = row[xfile_columns_index['Variant']]
    splited_variant = variant.split(":")
    resulted_row.append(splited_variant[0].replace('chrX', 'chr23'))
    resulted_row.append(splited_variant[1])

    for index,column_name in enumerate(output_header.split("\t")):
        if column_name in COLUMNS_MAPPING_DICT:
            column_name_xfile = COLUMNS_MAPPING_DICT[column_name]
            resulted_row.append(row[xfile_columns_index[column_name_xfile]])
        else:
            resulted_row.append('NA')

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
            output_header = []
            for fname in filenames:
                with open(fname,"rt",encoding="utf-8") as infile:
                    print(fname)
                    print('Loading data ...')
                    reader = csv.reader(infile, delimiter='\t')
                    header = next(reader)
                    header_row = "#chrom\tpos\t" + "\t".join(header)
                    if is_header_written is False:
                        output_header = header_row
                        out_file.write(header_row +'\n')
                        is_header_written = True
                    for row in reader:
                        # autosomal file
                        if len(row) == 24:
                            splited_variant = row[0].split(":")
                            row.insert(0, splited_variant[0])
                            row.insert(1, splited_variant[1])
                            line = f"\t".join(row)+"\n"
                            out_file.write(line)
                        # Xfile check
                        elif len(row) > 24:
                            line = generate_resulted_row(output_header, row, header)
                            out_file.write(line)
                        else:
                            print(f"Sorry! The file {fname} and {row} does not consist on proper tsv columns.")
                            exit(1)
                print(f"Finished!")
        except Exception as e:  # Catch any exception
            print(f"An error occurred: {e}")
            raise

# check the argument 
parser = argparse.ArgumentParser(description="The QC variant import script!")

parser.add_argument('input_file_path', type=str)
parser.add_argument('output_file_name', type=str)

args = parser.parse_args()

INPUT_FOLDER_PATH = args.input_file_path
if f"/{args.output_file_name}".endswith('.tsv'):
    OUTPUT_FOLDER_PATH = INPUT_FOLDER_PATH + f"/{args.output_file_name}"
    main_script(INPUT_FOLDER_PATH, OUTPUT_FOLDER_PATH)
else:
    print("Sorry, output file name should be tsv. e-g string.tsv")
    exit(1)

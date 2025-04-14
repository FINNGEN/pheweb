import os
import csv
import subprocess
from tqdm import tqdm
import time

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


def main_script():
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
                        # check if header is none output file
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
                        print(f"Sorry! The file {fname} does not consist on proper csv columns.")
                        exit(1)
            print(f"Finished!")

# convert tsv to gz using bgzip
def convert_tsv_to_gz(input_file, output_file):
    # Get the total size of the input file for progress calculation
    file_size = os.path.getsize(input_file)
    
    # Open the input file for reading and the output file for writing
    with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
        # Start bgzip process
        process = subprocess.Popen(
            ['bgzip', '-c', input_file],  # '-c' to write to stdout
            stdout=outfile,
            stderr=subprocess.PIPE
        )
        
        # Use tqdm to display progress based on file size
        with tqdm(total=file_size, unit='B', unit_scale=True, desc="Compressing") as pbar:
            # Read in chunks and update progress
            while True:
                chunk = infile.read(1024 * 1024)  # Read 1MB chunks
                if not chunk:
                    break
                outfile.write(chunk)
                pbar.update(len(chunk))
            
            # Wait for bgzip to finish
            process.wait()

        # # Check the process return code and handle accordingly
        if process.returncode == 0:
            print(f"Process succeeded with output: {output_gzipped_tsv}")
        else:
            print(f"Process failed with error: {process.returncode}")



# convert bgzip to tbi
def convert_gz_to_tbi():
    output_gz = output_gzipped_tsv
    # Step 1: Recompress the file using bgzip (ensure it is in BGZF format)
    bgzip_command = ['bgzip', '-c', output_gz]
    # output_gz = output_gzipped_tsv
    
    with open(output_gz, 'wb') as output_f:
        subprocess.run(bgzip_command, stdout=output_f)

    # Step 2: Index the BGZF file using tabix
    tabix_command = ['tabix', '-s', '1', '-b', '2', '-e', '2', output_gz]
    
    # Run the tabix command to generate the index (.tbi)
    subprocess.run(tabix_command)

    print(f"Index file created: {output_gz}.tbi")


main_script()
# convert_tsv_to_gz(output_fname, output_gzipped_tsv)
# convert_gz_to_tbi()




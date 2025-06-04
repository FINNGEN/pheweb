import os
import argparse
import gzip
import re

def generate_column_group(key, output_header):
    """
    generate resulted row after using dict mapping
    """
    print(key, output_header)
    return f"generate_column_group"

COLUMN= 'COLUMN';
VALUE= 'VALUE';

def map_row_with_header_index(row, header_index, output_file):
    output_writer = ''
    for header_row in header_index:
        new_row_dict = {
            key: row[idx] if isinstance(idx, int) and 0 <= idx < len(row) else idx
            for key, idx in header_row.items()
        }
        output_file.write("\t".join(str(v) for v in new_row_dict.values()) + "\n")
        # print(output_writer)
        # print('.', end='', flush=True)
        # print(header_row)
        # print(new_row_dict)

    # new_row_dict = {
    #     key: row[idx] if isinstance(idx, int) and 0 <= idx < len(row) else idx
    #     for key, idx in header_index[0].items()
    # }
    # print(header_index[0])
    # print(new_row_dict)
    # exit(1)
    return output_writer

def run(input_file, output_file):
    # write the array of objects to a csv file
    if os.path.exists(output_file):
        os.remove(output_file)  # Overwrite the file with an empty DataFrame
        print(f"File '{output_file}' is already exist, so it is cleared first to remove the old contents")
    # read in the files
    try:
        with open(output_file,"wt",encoding="utf-8") as output:
            # Read the first line (header)
            print('start indexing')
            with gzip.open(input_file, 'rt') as f:
                match_dict = {}
                resulted_index_header = []
                header = f.readline().strip().split('\t')
                for column in header:
                    if column ==  'FINNGENID':
                        continue
                    else:
                        pattern = re.compile(fr'^{column}_')
                        default_dict = {}
                        default_dict[header[0]] = 0
                        default_dict[COLUMN] = column
                        default_dict[VALUE] = header.index(column)
                        match_dict = {name: idx for idx, name in enumerate(header) if pattern.match(name)}
                        if (len(match_dict) > 0):
                            combined_dict = {**default_dict, **match_dict}
                            print('.', end='', flush=True)
                            #print(combined_dict)
                            new_data = {key.replace(f"{column}_", ''): value for key, value in combined_dict.items()}
                            #print(new_data)
                            resulted_index_header.append(new_data)
                print('Finished indexing and reading row data!')
                first_keys = resulted_index_header[0].keys()
                is_header_index_matched = all(set(d.keys()) == set(first_keys) for d in resulted_index_header)
                print(is_header_index_matched)
                if is_header_index_matched:
                    print('\t'.join(first_keys))
                    output_file_header = f"\t".join(first_keys)+"\n"
                    output.write(output_file_header)
                    for line in f:
                        row = line.strip().split('\t')
                        map_row_with_header_index(row, resulted_index_header, output)
                        ## output.write(map_row_with_header_index(row, resulted_index_header))
                    # row_dict = {
                    #         key: row[idx] if isinstance(idx, int) and 0 <= idx < len(row) else idx
                    #         for key, idx in resulted_index_header[0].items()
                    #     }
                    # print(resulted_index_header[0])
                    # print(row_dict)
                    # print(row[0])
                    # exit(1)
                # print(final_header_list)
                # for line in f:
                #     row = line.strip().split('\t')  # split by tab to get columns
                #     print(row)

    except Exception as e:  # Catch any exception
        print(f"An error occurred: {e}")
        raise

# check the argument 
parser = argparse.ArgumentParser(description="Convert the long format into short format!")
parser.add_argument('input_file_path', type=str)
parser.add_argument('output_file_name', type=str)

args = parser.parse_args()

if f"/{args.input_file_path}".endswith('.tsv.gz'):
    run(args.input_file_path, args.output_file_name)
else:
    print("Sorry, output file name should be tsv.gx. e-g string.tsv.gz")
    exit(1)

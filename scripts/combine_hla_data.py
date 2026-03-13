import gzip
import os
import sys

# get the full file path from the user
path = sys.argv[1]

# get filenames in hla/summary_stats folder
endpoints = list(map(lambda f: f.replace('.gz', ''), filter(lambda f: f.endswith('.gz'), os.listdir(f'{path}/'))))

with gzip.open('combined.gz', 'wt') as result_f:
    # write headers to combined file
    result_f.write('phenocode\tchrom\tpos\tref\talt\tpval\tmlogp\tbeta\tsebeta\taf_alt\taf_alt_cases\taf_alt_controls\n')
    for endpoint in endpoints:
        with gzip.open(f'{path}/{endpoint}.gz', 'rt') as f:
            f.readline()  # skip header
            for line in f:
                result_f.write(endpoint + '\t' + line)

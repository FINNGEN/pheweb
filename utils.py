
from __future__ import print_function, division, absolute_import

# Load config
import os.path
import imp
my_dir = os.path.dirname(os.path.abspath(__file__))
conf = imp.load_source('conf', os.path.join(my_dir, 'config.config'))

import re
import itertools
import math
import json
import gzip
import os
import errno
import random


def parse_variant(query, default_chrom_pos = True):
    if isinstance(query, unicode):
        query = query.encode('utf-8')
    chrom_pattern = r'(?:[cC][hH][rR])?([0-9]+)'
    chrom_pos_pattern = chrom_pattern + r'[-_:/ ]([0-9]+)'
    chrom_pos_ref_alt_pattern = chrom_pos_pattern + r'[-_:/ ]([-AaTtCcGg]+)[-_:/ ]([-AaTtCcGg]+)'

    match = re.match(chrom_pos_ref_alt_pattern, query) or re.match(chrom_pos_pattern, query) or re.match(chrom_pattern, query)
    g = match.groups() if match else ()

    if default_chrom_pos:
        if len(g) == 0: g += ('1',)
        if len(g) == 1: g += (0,)
    if len(g) >= 1: g = (g[0].lower(),) + g[1:]
    if len(g) >= 2: g = (g[0], int(g[1])) + tuple([bases.upper() for bases in g[2:]])
    return g + tuple(itertools.repeat(None, 4-len(g)))



def parse_marker_id(marker_id):
    match = parse_marker_id.regex.match(marker_id)
    if match is None:
        raise Exception("ERROR: MARKER_ID didn't match our MARKER_ID pattern: {!r}".format(marker_id))
    chr1, pos1, ref, alt, chr2, pos2 = match.groups()
    if chr1 != chr2 or pos1 != pos2:
        raise Exception("ERROR: chr:pos don't match between the two sides of MARKER_ID : {!r}".format(marker_id))
    return chr1, int(pos1), ref, alt
parse_marker_id.regex = re.compile(r'([^:]+):([0-9]+)_([-ATCG\.]+)/([-ATCG\.]+)_(?:chr)?([^:]+):([0-9]+)')

def make_marker_id(chrom, pos, ref, alt):
    return '{chrom}:{pos}_{ref}/{alt}_{chrom}:{pos}'.format(chrom=chrom, pos=pos, ref=ref, alt=alt)


def round_sig(x, digits):
    return 0 if x==0 else round(x, digits-1-int(math.floor(math.log10(abs(x)))))
assert round_sig(0.00123, 2) == 0.0012
assert round_sig(1.59e-10, 2) == 1.6e-10


def get_phenos_with_colnums(app_root_path):
    with open(os.path.join(app_root_path, 'data/phenos.json')) as f:
        phenos_by_phewas_code = {pheno['pheno_code']: pheno for pheno in json.load(f)}
    with gzip.open(conf.data_dir + '/matrix.tsv.gz') as f:
        header = f.readline().rstrip('\r\n').split('\t')
    assert header[:7] == '#chrom pos ref alt rsids nearest_genes maf'.split()
    for colnum, colname in enumerate(header[7:], start=7):
        if colname.startswith('pval-'):
            pheno_code = colname[len('pval-'):]
            phenos_by_phewas_code[pheno_code]['colnum_pval'] = colnum
    for pheno_code in phenos_by_phewas_code:
        assert 'colnum_pval' in phenos_by_phewas_code[pheno_code], (pheno_code, phenos_by_phewas_code[pheno_code])
    return phenos_by_phewas_code


pheno_fields_to_include_with_variant = {
    'phewas_string', 'category_name', 'num_cases', 'num_controls', 'num_samples',
}

def get_variant(query, phenos):
    import pysam
    # todo: differentiate between parse errors and variants-not-found
    chrom, pos, ref, alt = parse_variant(query)
    assert None not in [chrom, pos, ref, alt]

    tabix_file = pysam.TabixFile(conf.data_dir + '/matrix.tsv.gz')
    tabix_iter = tabix_file.fetch(chrom, pos-1, pos+1, parser = pysam.asTuple())
    for variant_row in tabix_iter:
        if int(variant_row[1]) == int(pos) and variant_row[3] == alt:
            matching_variant_row = tuple(variant_row)
            break
    else: # didn't break
        return None

    maf = round_sig(float(matching_variant_row[6]), 3)
    assert 0 < maf <= 0.5

    rv = {
        'variant_name': '{} : {:,} {}>{}'.format(chrom, pos, ref, alt),
        'chrom': chrom,
        'pos': pos,
        'ref': ref,
        'alt': alt,
        'maf': maf,
        'rsids': matching_variant_row[4],
        'nearest_genes': matching_variant_row[5],
        'phenos': [],
    }

    for pheno_code, pheno in phenos.iteritems():
        try:
            pval = float(matching_variant_row[pheno['colnum_pval']])
        except ValueError:
            pval = 1
        rv['phenos'].append({
            'phewas_code': pheno_code,
            'pval': pval,
        })
        for key in pheno:
            if key in pheno_fields_to_include_with_variant:
                rv['phenos'][-1][key] = pheno[key]
    return rv


def mkdir_p(path):
    # like `mkdir -p`
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST or not os.path.isdir(path):
            raise

def activate_virtualenv(path):
    with open(path) as f:
        code = compile(f.read(), path, 'exec')
        exec(code, dict(__file__=path))

def get_random_page():
    with open(os.path.join(conf.data_dir, 'top_hits.json')) as f:
        hits = json.load(f)
        hits = [hit for hit in hits if hit['pval'] < 5e-8]
    hit = random.choice(hits)
    r = random.random()
    if r < 0.4:
        return '/pheno/{}'.format(hit['pheno_code'])
    elif r < 0.8:
        return '/variant/{chrom}-{pos}-{ref}-{alt}'.format(**hit)
    else:
        return '/region/{pheno_code}/{chrom}-{pos}-{ref}-{alt}'.format(**hit)

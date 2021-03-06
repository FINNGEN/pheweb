
from ..utils import get_phenolist
from ..file_utils import MatrixReader, get_tmp_path, common_filepaths
from .cffi._x import ffi, lib

import os
import glob
import pysam

sites_filepath = common_filepaths['sites']
matrix_gz_filepath = common_filepaths['matrix']
matrix_gz_tmp_filepath = get_tmp_path(matrix_gz_filepath)

def should_run():
    cur_phenocodes = set(pheno['phenocode'] for pheno in get_phenolist())

    # Remove files that shouldn't be there (and will confuse the glob in matrixify)
    for filepath in glob.glob(common_filepaths['pheno']('*')):
        if os.path.basename(filepath) not in cur_phenocodes:
            os.remove(filepath)

    if not os.path.exists(matrix_gz_filepath): return True

    # check that the current matrix is composed of the correct columns/phenotypes.  If it's changed, rebuild the matrix.
    try:
        matrix_phenocodes = set(MatrixReader().get_phenocodes())
    except Exception:
        return True # if something broke, let's just rebuild the matrix.
    if matrix_phenocodes != cur_phenocodes:
        print('re-running because cur matrix has wrong phenos.')
        print('- phenos in pheno-list.json but not matrix.tsv.gz:', ', '.join(repr(p) for p in cur_phenocodes - matrix_phenocodes))
        print('- phenos in matrix.tsv.gz but not pheno-list.json:', ', '.join(repr(p) for p in matrix_phenocodes - cur_phenocodes))
        return True

    infilepaths = [common_filepaths['pheno'](phenocode) for phenocode in cur_phenocodes] + [sites_filepath]
    infile_modtime = max(os.stat(filepath).st_mtime for filepath in infilepaths)
    if infile_modtime > os.stat(matrix_gz_filepath).st_mtime:
        print('rerunning because some input files are newer than matrix.tsv.gz')
        return True

def run(argv):

    if should_run():
        args = [
            ffi.new('char[]', sites_filepath.encode('utf8')),
            ffi.new('char[]', common_filepaths['pheno']('*').encode('utf8')),
            ffi.new('char[]', matrix_gz_tmp_filepath.encode('utf8'))
        ]
        lib.cffi_make_matrix(*args)
        os.rename(matrix_gz_tmp_filepath, matrix_gz_filepath)
        pysam.tabix_index(
            filename=matrix_gz_filepath, force=True,
            seq_col=0, start_col=1, end_col=1 # note: these are 0-based, but `/usr/bin/tabix` is 1-based
        )
    else:
        print('matrix is up-to-date!')

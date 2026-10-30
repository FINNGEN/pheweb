import math
import re
import typing
from contextlib import closing

import pymysql
from google.cloud.exceptions import NotFound
from smart_open import open as smart_open

from .model import CodingDB
from .variant import Variant
from pheweb.serve.data_access.db_util import MysqlDAO

# inf enrichment values are stored as 1e300 in coding_variants_annotated
INF_ENRICHMENT = 1e300

# variant is formatted like Variant: chr-pos-ref-alt with 23 as X
RESULTS_SQL = """
    SELECT
        p.code AS phenocode,
        p.name AS phenostring,
        CONCAT(IF(a.chr = 23, 'X', a.chr), '-', a.pos, '-', a.ref, '-', a.alt) AS variant,
        a.af,
        a.info,
        a.rsid,
        a.most_severe,
        a.gene_most_severe,
        a.enrichment,
        s.mlogp_add,
        s.beta_add,
        s.sebeta_add,
        s.mlogp_chip_add,
        s.beta_chip_add,
        s.sebeta_chip_add,
        s.mlogp_chip_rec,
        s.beta_chip_rec,
        s.sebeta_chip_rec,
        -- strongest phenotype for each variant among the returned rows
        ROW_NUMBER() OVER (
            PARTITION BY s.variant_id ORDER BY s.max_mlogp DESC
        ) = 1 AS is_top_pheno
    FROM coding_summstats s
    JOIN phenotype p ON p.id = s.phenotype_id
    JOIN coding_variants_annotated a ON a.id = s.variant_id
"""

TOP_RESULTS_SQL = RESULTS_SQL + "WHERE s.max_mlogp > %s"

VARIANT_RESULTS_SQL = RESULTS_SQL + "WHERE a.chr = %s AND a.pos = %s AND a.ref = %s AND a.alt = %s"

GENE_RESULTS_SQL = RESULTS_SQL + "WHERE a.gene_most_severe = %s AND s.max_mlogp > %s"

PHENOTYPE_RESULTS_SQL = RESULTS_SQL + "WHERE p.code = %s"

# number of suggestions per type
AUTOCOMPLETE_LIMIT = 10

GENE_AUTOCOMPLETE_SQL = """
    SELECT DISTINCT gene_most_severe AS gene
    FROM coding_variants_annotated
    WHERE gene_most_severe LIKE %s
    ORDER BY gene_most_severe
    LIMIT %s
"""

# includes variants without results
VARIANT_AUTOCOMPLETE_SQL = """
    SELECT CONCAT(IF(chr = 23, 'X', chr), '-', pos, '-', ref, '-', alt) AS variant
    FROM coding_variants_annotated
    WHERE variant LIKE %s
    ORDER BY variant
    LIMIT %s
"""

PHENOTYPE_AUTOCOMPLETE_SQL = """
    SELECT code, name
    FROM phenotype
    WHERE code LIKE %s OR name LIKE %s
    ORDER BY code
    LIMIT %s
"""

CHROMOSOMES = {str(c): str(c) for c in range(1, 26)}
CHROMOSOMES.update({'X': '23', 'Y': '24', 'M': '25', 'MT': '25'})


def escape_like(value: str) -> str:
    return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def variant_prefix(query: str) -> typing.Optional[str]:
    """
    Convert a partial variant typed by the user (1-123-A, chrX_123, ...)
    into a prefix of the variant column (1:123:A, 23:123, ...).

    Returns None if the query does not start with a chromosome.
    """
    fields = re.split(r'[-:_|]', re.sub(r'^chr', '', query.strip(), flags=re.IGNORECASE))
    chrom = CHROMOSOMES.get(fields[0].upper().lstrip('0'))
    if chrom is None:
        return None
    return ':'.join([chrom] + [field.upper() for field in fields[1:]])


def format_row(row: dict) -> dict:
    """
    Format a joined summstats + annotation row into the flat
    row sent to the UI.
    """
    result = dict(row)
    # JSON has no infinity
    if result['enrichment'] is not None and result['enrichment'] >= INF_ENRICHMENT:
        result['enrichment'] = 'inf'
    result['rec_add'] = (row['mlogp_chip_rec'] - row['mlogp_add']
                         if row['mlogp_chip_rec'] is not None and row['mlogp_add'] is not None
                         else None)
    result['possible_explaining_signals'] = None
    # MySQL returns comparisons as 0/1
    result['is_top_pheno'] = bool(row['is_top_pheno'])
    return result


class CodingMysqlDAO(CodingDB, MysqlDAO):

    def __init__(self,
                 authentication_file,
                 plot_root: str,
                 path_format: str = "{plot_root}{variant}.raw.png",
                 top_threshold: float = 1e-5,
                 gene_threshold: typing.Optional[float] = None):
        MysqlDAO.__init__(self, authentication_file)
        self.plot_root = plot_root
        self.path_format = path_format
        self.top_threshold = top_threshold
        # None returns all results for a gene
        self.gene_threshold = gene_threshold
        self._top_results = None

    def get_top_results(self):
        # the data only changes on reload, so query once and cache
        if self._top_results is None:
            self._top_results = self._fetch_results(TOP_RESULTS_SQL,
                                                    (-math.log10(self.top_threshold),))
        return self._top_results

    def _fetch_results(self, sql: str, params: tuple):
        with closing(self.get_connection()) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
        return {'results': [format_row(row) for row in rows]}

    def get_by_variant(self, variant: Variant):
        return self._fetch_results(VARIANT_RESULTS_SQL,
                                   (variant.chr, variant.pos, variant.ref, variant.alt))

    def get_by_gene(self, gene: str):
        # max_mlogp is >= 0, so -1 keeps every row
        min_mlogp = -1 if self.gene_threshold is None else -math.log10(self.gene_threshold)
        return self._fetch_results(GENE_RESULTS_SQL, (gene, min_mlogp))

    def get_by_phenotype(self, phenocode: str):
        return self._fetch_results(PHENOTYPE_RESULTS_SQL, (phenocode,))

    def get_autocomplete(self, query: str):
        query = query.strip()
        if query == '':
            return []
        like = escape_like(query)
        prefix = variant_prefix(query)
        with closing(self.get_connection()) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(GENE_AUTOCOMPLETE_SQL, (like + '%', AUTOCOMPLETE_LIMIT))
                genes = cursor.fetchall()
                variants = []
                if prefix is not None:
                    cursor.execute(VARIANT_AUTOCOMPLETE_SQL, (escape_like(prefix) + '%', AUTOCOMPLETE_LIMIT))
                    variants = cursor.fetchall()
                cursor.execute(PHENOTYPE_AUTOCOMPLETE_SQL, (like + '%', '%' + like + '%', AUTOCOMPLETE_LIMIT))
                phenotypes = cursor.fetchall()
        return ([{'type': 'gene', 'value': row['gene'], 'label': row['gene']} for row in genes] +
                [{'type': 'variant', 'value': row['variant'], 'label': row['variant']} for row in variants] +
                [{'type': 'phenotype', 'value': row['code'], 'label': '{} ({})'.format(row['name'], row['code'])}
                 for row in phenotypes])

    def get_cluster_plot(self, variant):
        # plots are named chr_pos_ref_alt with 23 as X
        cpra = variant.split(':')
        if cpra[0] == '23':
            cpra[0] = 'X'
        path = self.path_format.format(plot_root=self.plot_root, variant='_'.join(cpra))
        try:
            with smart_open(path, 'rb') as file:
                return file.read()
        except (FileNotFoundError, NotFound):
            return None
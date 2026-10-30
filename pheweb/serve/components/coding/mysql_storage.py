import math
from contextlib import closing

import pymysql
from google.cloud.exceptions import NotFound
from smart_open import open as smart_open

from .model import CodingDB
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
                 top_threshold: float = 1e-5):
        MysqlDAO.__init__(self, authentication_file)
        self.plot_root = plot_root
        self.path_format = path_format
        self.top_threshold = top_threshold
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

    def get_by_variant(self, variant):
        pass

    def get_by_gene(self, gene):
        pass

    def get_results(self, index_range, query):
        pass
    
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
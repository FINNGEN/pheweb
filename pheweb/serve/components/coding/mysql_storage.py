import math
from contextlib import closing

import pymysql

from .model import CodingDAO, set_top_flags
from pheweb.serve.data_access.db_util import MysqlDAO

# inf enrichment values are stored as 1e300 in coding_variants_annotated
INF_ENRICHMENT = 1e300

# coding_variants_annotated column -> anno key returned to the UI
ANNO_COLUMNS = {
    'chr': 'chr',
    'pos': 'pos',
    'ref': 'ref',
    'alt': 'alt',
    'info': 'INFO',
    'af': 'AF',
    'ac_het': 'AC_Het',
    'ac_hom': 'AC_Hom',
    'af_chip': 'AF_chip',
    'ac_het_chip': 'AC_Het_chip',
    'ac_hom_chip': 'AC_Hom_chip',
    'most_severe': 'most_severe',
    'gene_most_severe': 'gene_most_severe',
    'rsid': 'rsid',
    'enrichment': 'enrichment',
}

# coding_summstats column -> result key returned to the UI
RESULT_COLUMNS = {
    'mlogp_add': 'mlogp_add',
    'beta_add': 'beta_add',
    'sebeta_add': 'sebeta_add',
    'mlogp_chip_add': 'mlogp_chip',
    'beta_chip_add': 'beta_chip',
    'sebeta_chip_add': 'sebeta_chip',
    'mlogp_chip_rec': 'mlogp_rec',
    'beta_chip_rec': 'beta_rec',
    'sebeta_chip_rec': 'sebeta_rec',
}

TOP_RESULTS_SQL = (
    "SELECT p.code, p.name, "
    + ", ".join(f"a.{c}" for c in ANNO_COLUMNS) + ", "
    + ", ".join(f"s.{c}" for c in RESULT_COLUMNS) + " "
    "FROM coding_summstats s "
    "JOIN phenotype p ON p.id = s.phenotype_id "
    "JOIN coding_variants_annotated a ON a.id = s.variant_id "
    "WHERE s.max_mlogp > %s"
)


def format_variant(chr: int, pos: int, ref: str, alt: str) -> str:
    # same format as Variant: chr-pos-ref-alt with 23 as X
    return "{}-{}-{}-{}".format('X' if chr == 23 else chr, pos, ref, alt)


def format_anno_value(column: str, value):
    if value is None:
        return 'NA'
    if column == 'enrichment' and value >= INF_ENRICHMENT:
        return 'inf'
    return value


class MySQLCodingDao(CodingDAO, MysqlDAO):

    def __init__(self, authentication_file, top_threshold: float = 1e-5):
        MysqlDAO.__init__(self, authentication_file)
        self.top_threshold = top_threshold
        self._top_results = None

    def get_top_results(self):
        # the data only changes on reload, so query once and cache
        if self._top_results is None:
            self._top_results = self._fetch_top_results(self.top_threshold)
        return self._top_results

    def _fetch_top_results(self, threshold: float):
        with closing(self.get_connection()) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(TOP_RESULTS_SQL, (-math.log10(threshold),))
                rows = cursor.fetchall()
        results = []
        anno = {}
        for row in rows:
            variant = format_variant(row['chr'], row['pos'], row['ref'], row['alt'])
            result = {'pheno': {'code': row['code'], 'name': row['name']}, 'variant': variant}
            result.update({key: row[column] for column, key in RESULT_COLUMNS.items()})
            result['possible_explaining_signals'] = None
            results.append(result)
            if variant not in anno:
                anno[variant] = {'variant': variant}
                anno[variant].update({key: format_anno_value(column, row[column])
                                      for column, key in ANNO_COLUMNS.items()})
        set_top_flags(results)
        return {
            'results': results,
            'anno': anno
        }

    def get_variant_range(self, query):
        pass

    def get_gene_range(self, query):
        pass

    def get_results(self, index_range, query):
        pass

    def get_cluster_plot(self, variant):
        pass

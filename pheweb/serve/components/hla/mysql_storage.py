import pymysql

from pheweb.serve.data_access.db_util import MysqlDAO
from pheweb.serve.components.hla.model import HLADB
from pheweb.serve.data_access.db_util import MysqlDAO

class HLAMySQLDao(HLADB, MysqlDAO):
    def __init__(self, authentication_file):
        MysqlDAO.__init__(self, authentication_file)

    def get_autocomplete(self):
        conn = self.get_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as c:
                c.execute("SELECT DISTINCT phenocode FROM hla", [])
                phenocode_result = c.fetchall()
                c.execute("SELECT DISTINCT alt FROM hla", [])
                alt_result = c.fetchall()
                c.execute("SELECT DISTINCT CONCAT('HLA-', SUBSTRING_INDEX(alt, '*', 1)) AS gene FROM hla", [])
                gene_result = c.fetchall()
        finally:
            conn.close()
        result = phenocode_result + alt_result + gene_result
        return result if len(result) != 0 else []

    def get_top_results(self):
        conn = self.get_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as c:
                sql = """SELECT *,
                    CONCAT('HLA-', SUBSTRING_INDEX(alt, '*', 1)) AS gene
                    FROM hla WHERE mlogp > 5
                    """
                c.execute(sql, [])
                result = c.fetchall()
        finally:
            conn.close()
        return result if len(result) != 0 else []

    def get_by_phenocode(self, phenocode):
        conn = self.get_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as c:
                sql = """SELECT *,
                    CONCAT('HLA-', SUBSTRING_INDEX(alt, '*', 1)) AS gene
                    FROM hla WHERE phenocode = %s
                    """
                c.execute(sql, [phenocode])
                result = c.fetchall()
        finally:
            conn.close()
        return result if len(result) != 0 else []
    
    def get_by_gene(self, gene):
        conn = self.get_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as c:
                sql = """SELECT *,
                    CONCAT('HLA-', SUBSTRING_INDEX(alt, '*', 1)) AS gene
                    FROM hla
                    WHERE CONCAT('HLA-', SUBSTRING_INDEX(alt, '*', 1)) = %s
                    """
                c.execute(sql, [gene])
                result = c.fetchall()
        finally:
            conn.close()
        return result if len(result) != 0 else []

    def get_by_variant(self, variant):
        conn = self.get_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as c:
                sql = """SELECT *,
                    CONCAT('HLA-', SUBSTRING_INDEX(alt, '*', 1)) AS gene
                    FROM hla WHERE alt = %s
                    """
                c.execute(sql, [variant])
                result = c.fetchall()
        finally:
            conn.close()
        return result if len(result) != 0 else []

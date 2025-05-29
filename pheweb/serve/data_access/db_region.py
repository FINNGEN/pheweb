import importlib.machinery
import typing
import abc
import pymysql
from pheweb.serve.data_access.db_util import MysqlDAO
from contextlib import closing
import re
from typing import List, Dict, Union
import json
from pheweb.serve.components.colocalization.finngen_common_data_model.genomics import Locus as Region

class DBRegionDAO(object):

    @abc.abstractmethod
    def get_phenotypes():
        return
    
    @abc.abstractmethod
    def get_region(self, phenotype: str, region: Region):
        return
    
    @abc.abstractmethod
    def get_region_summary(self, phenotype: str, region: Region):
        return

    @abc.abstractmethod
    def get_locuszoom_results(self, phenotype: str, locus : str):
        return


class MYSQLRegionDAO(DBRegionDAO, MysqlDAO):
    def __init__(self,
                 authentication_file : str,
                 parameters: Dict[str, Union[str, List[str]]]
     ):
        super(DBRegionDAO, self).__init__(authentication_file=authentication_file)
        self._parameters = parameters


    def get_phenotypes(self):
        with closing(self.get_connection()) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                table = self._parameters['phenotype_table']
                sql = f"""SELECT *
                          FROM {table}"""
                parameters = []
                cursor.execute(sql, parameters)
                return cursor.fetchall()

    
    def get_region(self, phenotype: str, region: Region):
        with closing(self.get_connection()) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                table = self._parameters['region_table']
                sql = f"""SELECT * 
                          FROM {table} WHERE 
                          phenotype = %s and
                          region_chromosome = %s and
                          (region_end >= %s and region_start <= %s)"""
                parameters = [phenotype,
                              region.chromosome,
                              region.start,
                              region.stop]
                cursor.execute(sql, parameters)
                return cursor.fetchall()

    def get_region_summary(self, phenotype: str, region: Region):
        with closing(self.get_connection()) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                table = self._parameters['region_summary_table']
                columns = ', '.join(f'{v} as "{k}"' for k, v in self._parameters['region_summary_columns'].items())
                sql = f"""SELECT {columns}
                          FROM {table} WHERE 
                          phenotype = %s and
                          region_chromosome = %s and
                          (region_end >= %s and region_start <= %s)"""
                parameters = [phenotype,
                              region.chromosome,
                              region.start,
                              region.stop]
                cursor.execute(sql, parameters)
                rows = cursor.fetchall()
                return rows

    def get_locuszoom_results(phenotype: str, region: Region):
        return

import importlib.machinery
import typing
import abc
import pymysql
from pheweb.serve.data_access.db_util import MysqlDAO
from contextlib import closing
import re
from typing import List, Dict, Union
from pheweb.serve.models.genomics import Region 
import click
import json

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
                          region_start >= %s and %s >= region_end"""
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
                          region_start >= %s and %s >= region_end"""
                parameters = [phenotype,
                              region.chromosome,
                              region.start,
                              region.stop]    
                cursor.execute(sql, parameters)
                rows = cursor.fetchall()
                return rows

    def get_locuszoom_results(phenotype: str, region: Region):
        return

@click.group()
def cli():
    """db region CLI"""
    pass

def init_options(f):
    f = click.option("--authentication_file", type=click.Path(exists=True, dir_okay=False, readable=True), help='authentication credential file')(f)
    f = click.option("--parameter_file", required=True, type=click.Path(exists=True, dir_okay=False, readable=True), help='parameter file')(f)
    return f

def common_options(f):
    f = init_options(f)
    f = click.option('--phenotype', required=True, help='phenotype')(f)
    f = click.option('--chromosome', required=True, type=int, help='chromosome region')(f)
    f = click.option('--start', required=True, type=int, help='start region')(f)
    f = click.option('--stop', required=True, type=int, help='stop region')(f)
    return f

@cli.command()
@common_options
def get_locuszoom_results(authentication_file, parameter_file, phenotype, chromosome, start, stop):
    region = Region(chromosome, start, stop)
    with open(parameter_file) as f:
        print(parameter_file)
        parameters = json.load(f)
    dao = MYSQLRegionDAO(authentication_file, parameters)
    print (dao.get_locuszoom_results())

@cli.command()
@common_options
def get_region_summary(authentication_file, parameter_file, phenotype, chromosome, start, stop):
    region = Region(chromosome, start, stop)
    with open(parameter_file) as f:
        print(parameter_file)
        parameters = json.load(f)
    dao = MYSQLRegionDAO(authentication_file, parameters)
    print(json.dumps(dao.get_region_summary(phenotype, region), indent=4))

@cli.command()
@common_options
def get_region(authentication_file, parameter_file, phenotype, chromosome, start, stop):
    region = Region(chromosome, start, stop)
    with open(parameter_file) as f:
        print(parameter_file)
        parameters = json.load(f)
    dao = MYSQLRegionDAO(authentication_file, parameters)
    print(json.dumps(dao.get_region(phenotype, region), indent=4))
    
@cli.command()
@init_options
def get_phenotypes(authentication_file, parameter_file):
    with open(parameter_file) as f:
        print(parameter_file)
        parameters = json.load(f)
    dao = MYSQLRegionDAO(authentication_file, parameters)
    print(json.dumps(dao.get_phenotypes(), indent=4))
    
if __name__ == '__main__':
    cli()

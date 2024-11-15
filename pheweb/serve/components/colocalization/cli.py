import typing
import click
import os
import typing
import csv
import time
import attr
import functools

from attr.validators import instance_of
from pheweb.serve.components.colocalization.model_db import ColocalizationDAO
from flask.cli import AppGroup, with_appcontext

# TOOO : write documentation
# TODO : fix name of dump

data_cli = AppGroup('colocalization', short_help="Colocalization commands")

@attr.s
class DAOContext(object):
    db_url = attr.ib(validator=instance_of(str))
    parameters = attr.ib(default={})
    timer = attr.ib(default=True)
    echo = attr.ib(default=True)
    def __enter__(self):
        self.start_timer = time.perf_counter()

        self.dao = ColocalizationDAO(db_url = self.db_url,
                                     parameters = self.parameters,
                                     echo = self.echo)
        return self.dao

    def __exit__(self, *exc):
        if(self.timer):
            end_timer = time.perf_counter()
            delta = round((end_timer - self.start_timer) * 1000000)
            print("context took {0} ms ".format(delta))
        del self.dao


@data_cli.command("init", short_help="create schema")
@click.argument("path", required=True, type=str)
@with_appcontext
def init_command(path) -> None:
    with DAOContext(path) as dao:
        dao.create_schema()

@data_cli.command("schema", short_help="output schema")
@click.argument("path", required=True, type=str)
@with_appcontext
def schema_command(path) -> None:
    with DAOContext(path, timer = False) as dao:
        dao.dump()

@data_cli.command("delete", short_help="delete data and drop tables")
@click.argument("path", required=True, type=str)
@with_appcontext
def delete_command(path) -> None:
    with DAOContext(path) as dao:
        dao.delete_all()


@data_cli.command("debug", short_help="start a debug session")
@with_appcontext
def harness() -> None:
    from pheweb.serve.components.colocalization.finngen_common_data_model.colocalization import Colocalization
    print(Colocalization.columns())

    import pdb; pdb.set_trace()


@data_cli.command("load", short_help="load data file")
@click.argument("release", required=True, type=int)
@click.argument("path", required=True, type=str)
@click.argument("data", required=True, type=str)
@click.option('--header/--no-header', default=True)
@with_appcontext
def cli_load(release: int, path: str, data: str, header: bool) -> None:
    with DAOContext(path, echo=False) as dao:
        print("loaded {0} entries from : '{1}' ".format(dao.load_data(release, data, header = header),path))

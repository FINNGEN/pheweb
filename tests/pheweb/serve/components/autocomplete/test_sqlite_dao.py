import os
import pytest
from contextlib import closing

from pheweb.serve.components.autocomplete.sqlite_dao import get_sqlite3_readonly_connection, GeneAliasesSqliteDAO

def get_file_path(filename : str) -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)

TEST_DATABASE=get_file_path("data/gene_aliases.sqlite3")

@pytest.mark.unit
def test_parse_variant() -> None:
    with get_sqlite3_readonly_connection(TEST_DATABASE) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute('SELECT 1')
            row = list(cursor.fetchone())
            assert row == [1]
    

@pytest.mark.unit
def test_get_gene_aliase() -> None:
    dao=GeneAliasesSqliteDAO(filepath=TEST_DATABASE)
    assert dao.get_gene_aliases("101F10.1") == {'KNOP1'}
    assert dao.get_gene_aliases("") == set()
    assert dao.get_gene_aliases("101F10") == set()
    assert dao.get_gene_aliases("101f10.1") == {'KNOP1'}


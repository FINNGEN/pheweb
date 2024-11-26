#!/bin/env python3
import csv
import json
import os
import re
import shutil
import sqlite3
import sys
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Tuple

from pheweb.file_utils import get_filepath, get_tmp_path
from pheweb.load import download_genes
from pheweb.utils import PheWebError


def get_gene_tuples_with_ensg() -> Iterator[Tuple[str,int,int,str,str]]:
    with open(get_filepath('genes')) as f:
        for row in csv.reader(f, delimiter='\t'):
            yield (row[0], int(row[1]), int(row[2]), row[3], row[4])

def get_genenamesorg_ensg_aliases_map(ensgs_to_consider: Iterable[str]) -> Dict[str, List[str]]:
    ensgs_to_consider = set(ensgs_to_consider)
    r = urllib.request.urlopen('http://ftp.ebi.ac.uk/pub/databases/genenames/out_of_date_hgnc/json/non_alt_loci_set.json')
    data = r.read().decode('utf-8')
    ensg_to_aliases = {}
    for row in json.loads(data)['response']['docs']:
        try:
            if not row.get('ensembl_gene_id',None) or row['ensembl_gene_id'] not in ensgs_to_consider: continue
            assert re.match(r'^ENSG[R0-9\.]+$', row['ensembl_gene_id']), row
            aliases = [row['symbol']] + row.get('prev_symbol',[]) + row.get('alias_symbol',[])
            aliases = [alias for alias in aliases if alias != '']
            aliases = [alias for alias in aliases if re.match(r'^[-\._a-zA-Z0-9]+$', alias)]
            ensg_to_aliases[row['ensembl_gene_id']] = aliases
        except Exception:
            raise PheWebError('Cannot handle genenames row: {}'.format(row))
    return ensg_to_aliases

def get_alias_canonicals() -> Dict[str,List[str]]:
    # NOTE: "canonical" refers to the canonical symbol for a gene
    genes = [{'canonical': canonical, 'ensg':ensg} for _,_,_,canonical,ensg in get_gene_tuples_with_ensg()]
    assert len({g['ensg'] for g in genes}) == len(genes)
    assert len({g['canonical'] for g in genes}) == len(genes)
    print('num canonical gene names: {}'.format(len(genes)))

    canonicals_upper = {g['canonical'].upper() for g in genes}
    ensg_to_canonical = {g['ensg']: g['canonical'] for g in genes}
    ensg_to_aliases = get_genenamesorg_ensg_aliases_map(g['ensg'] for g in genes)
    canonical_to_aliases = {ensg_to_canonical[ensg]: ensg_to_aliases.get(ensg, []) for ensg in ensg_to_canonical.keys()}
    for canonical, aliases in canonical_to_aliases.items():
        aliases = [alias for alias in aliases if alias.upper() not in canonicals_upper]
        aliases.append(canonical.upper())
        aliases = list(set(aliases))
        canonical_to_aliases[canonical] = aliases

    alias_to_canonicals:Dict[str,List[str]] = {}
    for canonical, aliases in canonical_to_aliases.items():
        for alias in aliases:
            alias_to_canonicals.setdefault(alias, []).append(canonical)
    return alias_to_canonicals

def get_gene_aliases() -> Iterator[Tuple[str,str]]:
    for alias,canonicals in get_alias_canonicals().items():
        yield (alias, ','.join(canonicals))

def get_key_name_lookup() -> Iterator[Tuple[str,str]]:
    """
    Yields:
        Tuple[str, str]: A tuple where:
            - The first element is the 'key', a normalized uppercase term used for searching.
            - The second element is the 'name', an acceptable gene name associated with the key.
            This includes yielding:
                - The alias in uppercase as a key with itself as the name.
                - Each canonical name in uppercase as a key with the alias as the name.
                - The alias in uppercase as a key with each canonical name as the name.

    Examples:
        Assuming `get_alias_canonicals()` returns {'tp53': ['p53', 'TPM53']},
        the generator will yield:
            ('TP53', 'tp53')
            ('P53', 'tp53')
            ('TP53', 'p53')
            ('TPM53', 'tp53')
            ('TP53', 'TPM53')
    """
    for alias,canonicals in get_alias_canonicals().items():
        yield (alias, alias)
        for c in canonicals:
            yield (c, alias)
            yield (alias, alias)
            yield (alias, c)

def download_gene_aliases() -> None:
    aliases_filepath = Path(get_filepath('gene-aliases-sqlite3', must_exist=False)())
    parent = aliases_filepath.parent
    if not parent.exists(): parent.mkdir(parents=False, exist_ok=True)
    aliases_tmp_filepath = Path(get_tmp_path(aliases_filepath))
    print('gene aliases will be stored at {!r}'.format(str(aliases_filepath)))
    if aliases_tmp_filepath.exists(): aliases_tmp_filepath.unlink()
    db = sqlite3.connect(str(aliases_tmp_filepath), isolation_level=None)

    db.execute("PRAGMA mmap_size = 30000000000;")
    db.execute("PRAGMA page_size = 32768;")

    db.execute("PRAGMA journal_mode = OFF;")
    db.execute("PRAGMA synchronous = 0;")
    db.execute("PRAGMA cache_size = 1000000;")
    db.execute("PRAGMA locking_mode = EXCLUSIVE;")
    db.execute("PRAGMA temp_store = MEMORY;")

    with db:
        db.execute('CREATE TABLE gene_aliases (alias TEXT PRIMARY KEY, canonicals_comma TEXT)')
        db.executemany('INSERT INTO gene_aliases VALUES (?,?)', sorted(get_gene_aliases()))
        db.execute('CREATE TEMPORARY TABLE key_name_temporary (key TEXT, name TEXT)')
        db.executemany('INSERT INTO key_name_temporary VALUES (?,?)', sorted(get_key_name_lookup()))
        db.execute('CREATE TABLE key_name as SELECT DISTINCT * FROM key_name_temporary')
        db.execute('CREATE INDEX key_name_key_idx ON key_name (key)')
        aliases_tmp_filepath.replace(aliases_filepath)

def run(argv:List[str]) -> None:
    if '-h' in argv or '--help' in argv:
        print('Make a database of all gene names and their aliases for easy searching.')
        exit(1)

    # This needs genes for filtering
    gene_filepath = Path(get_filepath('genes', must_exist=False))
    if not gene_filepath.exists():
        print('Downloading genes')
        download_genes.run([])
    else:
        print("getting an existing bed file: {}".format(gene_filepath))
        genes = [{'canonical': canonical, 'ensg': ensg.split('.')[0]} for _,_,_,canonical,ensg in get_gene_tuples_with_ensg()]
        assert len({g['ensg'] for g in genes}) == len(genes), f'Detected duplicates in gene symbols in the provided genes file {format(gene_filepath)}'
        assert len({g['canonical'] for g in genes}) == len(genes), 'Detected duplicates in ensembl gene ids in the provided genes file {}'.format(gene_filepath)

    dest_filepath = Path(get_filepath('gene-aliases-sqlite3', must_exist=False)())
    print(f"sqlite filename: {dest_filepath}")
    if dest_filepath.exists(): return
    download_gene_aliases()
    print('Done')

if __name__ == "__main__":
    run(sys.argv[1:])

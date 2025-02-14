#!/bin/env python3
import pymysql
from functools import reduce
import pandas as pd
import json
from collections import defaultdict
from pathlib import Path
from pheweb.serve.data_access.finemapping_susie import parse_susie, parse_susie_summary
from pheweb.serve.data_access.finemapping_conditional import parse_conditional
from pheweb.serve.data_access.finemapping_finemap import parse_finemap
from pheweb.serve.data_access.finemapping import lead_variants
import numpy as np
from itertools import chain

# Database connection details
host = '127.0.0.1'
user = 'pheweb_production'
password = 'noo9ahV[ei'
database = 'analysis_r12'

base_paths = { "susie": "/data/pheweb/r12/data/finemapping/snp",
               "conditional": "/mnt/r12/pheweb/r12/release/finemap/conditional",
               "finemap": "/mnt/r12/pheweb/r12/release/finemap/cred" }

def query_database(phenocode,
                   chromosome,
                   start_position,
                   end_position):
    # Connect to the MySQL database
    connection = pymysql.connect(host=host,
                                  user=user,
                                  password=password,
                                  database=database)
    try:
        finemapped_region_type = 'all'
        with connection.cursor(pymysql.cursors.DictCursor) as cursori:
            if finemapped_region_type == "all":
                where_sql = ""
            elif finemapped_region_type == "conditional":
                where_sql = " AND (type='conditional') "
            elif finemapped_region_type == "finemapping":
                where_sql = " AND (type='susie' OR type='finemap') "
            else:
                raise ValueError(f'unsupported type "{finemapped_region_type}"')
            # db.py:get_max_region
            sql = f"""WITH bounds AS (SELECT min(start) AS min_start, 
                                             max(end)   AS max_end,
                                             phenocode  AS phenocode,
                                             chr        AS chr
                                      FROM finemapped_regions 
                                      WHERE phenocode=%s AND chr=%s AND start <= %s AND end >= %s)
                      SELECT finemapped_regions.type, 
                             finemapped_regions.chr, 
                             finemapped_regions.start, 
                             finemapped_regions.end, 
                             finemapped_regions.n_signals, 
                             finemapped_regions.variants,
                             finemapped_regions.path 
                      FROM finemapped_regions , bounds
                      WHERE 
                      finemapped_regions.phenocode=bounds.phenocode AND 
                      finemapped_regions.chr=bounds.chr AND 
                      finemapped_regions.start <= bounds.min_start AND 
                      finemapped_regions.end >= bounds.max_end 
                      {where_sql}
                      ORDER BY type DESC
                      """
            cursori.execute(sql,
                            [phenocode, chromosome, end_position, start_position])
            result = cursori.fetchall()
            for res in result:
                res["path"] = f'{base_paths[res["type"]]}/{res["path"]}'
                if res["type"] == "conditional":
                    variants = res["variants"].split(",")
                    res["conditioned_on"] = list(reduce(lambda acc, x: acc + [f"{acc[-1]},{x}" if acc else x], variants, []))
                    res["paths"] = [f'{res["path"]}{variants[0]}_{str(i+1)}.conditional' for i, _ in enumerate(variants)]
                else:
                    res["paths"] = [res["path"]]
                res["variants"] = list(chain.from_iterable(map(lead_variants(res), res["paths"])))
        return result
    finally:
        connection.close()

def main():
    phenocode = 'AUTOIMMUNE'
    chromosome = 16
    start_position = 28784341
    end_position = 28884341
    # 16:28784341-28884341
    # https://bdev.finngen.fi/region/AUTOIMMUNE/16:28784341-28884341
    message = query_database(phenocode,
                             chromosome,
                             start_position,
                             end_position)
    print(json.dumps(message))

if __name__ == "__main__":
    main()


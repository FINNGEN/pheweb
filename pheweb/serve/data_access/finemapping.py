from functools import reduce
import pandas as pd
import json
from collections import defaultdict
from pathlib import Path
from pheweb.serve.data_access.finemapping_susie import parse_susie, parse_susie_summary
from pheweb.serve.data_access.finemapping_conditional import parse_conditional
from pheweb.serve.data_access.finemapping_finemap import parse_finemap
import numpy as np
from itertools import chain

def df_min(df, column : str):
    row = df.loc[df[column].idxmin()]
    row = row.map(lambda x: int(x) if isinstance(x, (int, np.integer)) else (None if pd.isna(x) else x))
    result = row.to_dict()
    return result

def df_list(df):
    data = df.applymap(lambda x: int(x) if isinstance(x, (int, np.integer)) else (None if pd.isna(x) else x))
    result = data.replace({np.nan: None}).to_dict(orient='records')
    result = list(result)
    return result

def finemap_lead_variant(region, path):
    df = parse_finemap(path)
    df = df[(df.chr == int(region['chr'])) & (df.position <= int(region['end'])) & (df.position >= int(region['start']))]
    df = df.loc[df.groupby('cs')['prob'].idxmin()]
    result = df_list(df)
    return result

def conditional_lead_variant(region, path):
    df = parse_conditional(path)
    result = df_min(df, 'pvalue')
    return  [result]


def susie_lead_variant(region):
    data = parse_susie(region)
    data = df_list(data)
    return data

def lead_variants(region):
    finemapped_region_type = region["type"]
    def handler(path):
        if finemapped_region_type == "conditional":
            return conditional_lead_variant(region, path)
        elif finemapped_region_type == "finemap":
            return finemap_lead_variant(region, path)
        elif finemapped_region_type == "susie":
            return susie_lead_variant(region)
        else:
            raise ValueError(f'unsupported type "{finemapped_region_type}"')
    return handler


def region_summary(region):
    if region["type"] == "conditional":
        variants = region["variants"].split(",")
        region["conditioned_on"] = list(reduce(lambda acc, x: acc + [f"{acc[-1]},{x}" if acc else x], variants, []))
        region["paths"] = [f'{region["path"]}{variants[0]}_{str(i+1)}.conditional' for i, _ in enumerate(variants)]
    else:
        region["paths"] = [region["path"]]
    region["lead_variants"] = list(chain.from_iterable(map(lead_variants(region), region["paths"])))
    del(region["paths"], region["path"])
    return region
    
def extract_variants(region):
    finemapped_region_type = region["type"]
    def handler(path):
        if finemapped_region_type == "conditional":
            return conditional_data(region, path)
        elif finemapped_region_type == "finemap":
            return finemap_data(region, path)
        elif finemapped_region_type == "susie":
            data = parse_susie(region)
            data = data.applymap(lambda x: int(x) if isinstance(x, (int, np.integer)) else x)
            result = data.to_dict(orient='records')
            return list(result)
        else:
            raise ValueError(f'unsupported type "{finemapped_region_type}"')
    return handler

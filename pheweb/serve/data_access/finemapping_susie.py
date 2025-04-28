from pathlib import Path
import pandas as pd

def parse_susie_summary(path, region, prob_threshold=-1):
    if Path(path).is_file():
        data = pd.read_csv(path, sep='\t')
        data = data[(data.region == region) & (data.prob > prob_threshold)]
        data['id'] = data['v'] = data['v'].replace('X','23')
        data[['chr', 'position', 'ref', 'alt']] = data['v'].str.split(':', expand=True)
        result_map = {
            f"{row['v']}": row.to_dict()
            for _, row in data.iterrows()
        }
    else:
        result_map = {}
    return result_map

def format_rsid(row):
    return f"chr{row['chr']}_{row['position']}_{row['ref']}_{row['alt']}"
    
def parse_susie_filter(path, region, prob_threshold=-1):
    data = pd.read_csv(path, sep='\t')
    columns = {'chromosome': 'chr',
               'allele1': 'ref',
               'allele2': 'alt',
               'v': 'id',
               'cs_specific_prob': 'prob'}
    data.rename(columns = columns, inplace=True)
    data = data[(data.region == region) & (data.prob > prob_threshold)]
    data['chr'] = data['chr'].str.replace('chr', '').replace('X','23')
    data['id'] = data['id'].replace('X','23')
    data['rsid'] = data.apply(format_rsid , axis=1)
    result_map = {
        f"{row['id']}": row.to_dict()
        for _, row in data.iterrows()
    }
    return result_map

def parse_susie(region, prob_threshold=-1):
    
    summary_path = region['path'].replace("snp.filter", "cred.summary")
    filter_path = region['path']
    
    current_region = f"chr{str(region['chr'])}:{region['start']}-{region['end']}"
    summary_data = parse_susie_summary(summary_path, current_region, prob_threshold)
    filter_data = parse_susie_filter(filter_path, current_region, prob_threshold)
    
    result_map = {k: {**v, **filter_data.get(k, {})} for k, v in summary_data.items()}
    
    expected_columns = ['id',
                        'rsid',
                        'chr',
                        'position',
                        'ref',
                        'alt',
                        'maf',
                        'prob',
                        'cs',
                        'low_purity']
    data = pd.DataFrame(result_map.values(),columns=expected_columns)
    data.prob = data.prob.round(3)
    data = data.where(pd.notna(data), None)
    return data


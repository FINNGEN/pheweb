import pandas as pd

def parse_conditional(path,
                      prob_threshold : float=1):
    df = pd.read_csv(path, sep=' ')
    df = df[df['p.value_cond'].astype(float) <= prob_threshold]
    
    # Transformations
    df['id'] = df['SNPID'].str.replace('chr', '', regex=False).str.replace('X', '23', regex=False)
    df['id'] = df['id'].astype(str).replace('_', ':').apply(lambda x: x[::-1].replace('_', '/', 1)[::-1])
    
    df['varid'] = df['rsid'].astype(str).replace('chr', '', regex=False).str.replace('_', ':', regex=False).str.replace('X', '23', regex=False)
    df['chr'] = df['CHR'].astype(str).replace('chr', '', regex=False)
    df['position'] = df['POS'].astype(int)
    df['end'] = df['POS'].astype(int)
    df['ref'] = df['Allele1']
    df['alt'] = df['Allele2']
    df['maf'] = df['AF_Allele2'].astype(float)
    df['pvalue'] = df['p.value_cond'].astype(float)
    df['beta'] = df['BETA_cond'].astype(float).round(3)
    df['sebeta'] = df['SE_cond'].astype(float).round(3)
    
    # Select and return relevant columns
    df = df[['id', 'varid', 'chr', 'position', 'end', 'ref', 'alt', 'maf', 'pvalue', 'beta', 'sebeta']]
    return df

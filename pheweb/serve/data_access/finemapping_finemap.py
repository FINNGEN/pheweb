import pandas as pd

def parse_finemap_dict_list(path : str):
    data = { 'id': [],
             'chr': [],
             'position': [],
             'ref': [],
             'alt': [],
             'prob': [],
             'cs': [] }
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or line.startswith('index'):
                continue

            fields = line.split(' ')
            for i in range(0, int((len(fields) - 1) / 2)):
                if fields[i * 2 + 1] != 'NA':
                    cpra = fields[i * 2 + 1].split('_')
                    chrom = cpra[0].replace('chr', '').replace('X', '23')
                    
                    data['id'].append(f"{chrom}:{cpra[1]}_{cpra[2]}/{cpra[3]}")
                    data['chr'].append(int(chrom))
                    data['position'].append(int(cpra[1]))
                    data['ref'].append(cpra[2])
                    data['alt'].append(cpra[3])
                    data['prob'].append(round(float(fields[i * 2 + 2]), 3))
                    data['cs'].append(int(i + 1))
    return data
                       

def parse_finemap(path : str):
    data = parse_finemap_dict_list(path)
    return pd.DataFrame(data)

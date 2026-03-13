import gzip
import sys
import pymysql
import importlib.machinery

auth_file_path = sys.argv[1]
authentication_file = auth_file_path if auth_file_path.endswith('.conf') else f'{auth_file_path}/mysql.conf'
file_name = sys.argv[2] if len(sys.argv) > 2 else 'combined.gz'

def create_connection(host, user, password, db, port=None) -> object:
    kwargs = {'port': port} if port is not None else {}
    connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
            **kwargs
        )
    return connection

loader = importlib.machinery.SourceFileLoader('mysql_auth', authentication_file)
auth_module = loader.load_module()

db_user = getattr(auth_module, 'mysql')['user']
db_password = getattr(auth_module, 'mysql')['password']
db_host = getattr(auth_module, 'mysql')['host']
db = getattr(auth_module, "mysql")['db']
db_port = getattr(auth_module, "mysql").get('port', None)

cnx = create_connection(db_host, db_user, db_password, db, db_port)
cursor = cnx.cursor()

# load the summary data into pheweb.hla table
with gzip.open(file_name, 'rt') as f:
    next(f)  # skip header
    for line in f:
        try:
            phenocode, chrom, pos, ref, alt, pval, mlogp, beta, sebeta, af_alt, af_alt_cases, af_alt_controls = line.strip().split('\t')
        except:
            phenocode, chrom, pos, ref, alt, pval, mlogp, beta, sebeta, af_alt = line.strip().split('\t')
            af_alt_cases, af_alt_controls = None, None
        cursor.execute('INSERT INTO hla (phenocode, chrom, pos, ref, alt, pval, mlogp, beta, sebeta, af_alt, af_alt_cases, af_alt_controls) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (phenocode, chrom, pos, ref, alt, pval, mlogp, beta, sebeta, af_alt, af_alt_cases, af_alt_controls))
cnx.commit()
cnx.close()
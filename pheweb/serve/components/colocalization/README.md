# pheweb-colocalization
pheweb colocalization

# Quick start

Install packages

```
   pip install .
```

Setup environment


```
   export FLASK_APP=pheweb/serve/components/colocalization/app.py
   export PYTHON_PATH=.
   export RELEASE=10
```


## Setting up your development database



The standard sqlalchemy [database url](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls) are supported.
Set your uri :

```
export SQLALCHEMY_DATABASE_URI=
```


In addition the path of a mysql configuration file can be specified and is often used :

```
	export SQLALCHEMY_DATABASE_URI=/tmp/mysql.conf
```

mysql conf template:

```conf
mysql = {
     'host': 'RETRACTED',
     'db': 'RETRACTED',
     'user': 'RETRACTED',
     'password': 'RETRACTED',
     'release': 10
}
```

Setting up a sqlite database is a convient to setup :


```
     export SQLALCHEMY_DATABASE_URI=sqlite:////tmp/tmp.db # setup environment
```

Create the database schema if it doesn't exist the database :


```
     flask colocalization init ${SQLALCHEMY_DATABASE_URI} # create schema
```

Load a colocalization file into your database (has to start with a slash) :

The order of columns of the file to be loaded are specified below.

> source1, source2, pheno1, pheno1\_description, pheno2, pheno2\_description, quant1, quant2, tissue1, tissue2, locus_id1, locus\_id2, chrom, start, stop, clpp, clpa, vars, len_cs1, len\_cs2, len_inter, vars1\_info, vars2\_info 

The following command may help rearrange columns.

```
cat $FILE | sqlite3 -csv ':memory:' '.headers on' '.separator "\t"' '.mode tabs' '.import /dev/stdin data' 'select source1, source2, pheno1, pheno1\_description, pheno2, pheno2\_description, quant1, quant2, tissue1, tissue2, locus_id1, locus\_id2, chrom, start, stop, clpp, clpa, vars, len_cs1, len\_cs2, len_inter, vars1\_info, vars2\_info from data' 
```


```
     flask colocalization load ${RELEASE} ${SQLALCHEMY_DATABASE_URI} <datafile> # load data file into database
```

If you wish to delete the colocalization data from the database :

```
     flask colocalization delete ${SQLALCHEMY_DATABASE_URI} # delete schema
```


Additional commands

```
	 flask colocalization --help # command help
	 flask colocalization schema ${SQLALCHEMY_DATABASE_URI} # output schema
```


The endpoints

```
     # Get the list of phenotypes
     curl http://127.0.0.1:5000/api/colocalization
     # examples
     # export PHENOTYPE=AB1_ARTHROPOD
     # export LOCUS=1_115975000_115977000
     # export COLOCALIZATION_ID=1
     # colocalization results for locus
     curl http://127.0.0.1:5000/api/colocalization/$PHENOTYPE/$LOCUS
     # summary of colocalization results for locus
     curl http://127.0.0.1:5000/api/colocalization/$PHENOTYPE/$LOCUS/summary
     # this end point use used for lozus zoom
     curl http://127.0.0.1:5000/api/colocalization/$PHENOTYPE/$LOCUS/finemapping
     # get specific colocolization record 
     curl http://127.0.0.1:5000/api/colocalization/$COLOCALIZATION_ID
```

# Development
	
	
Install packages

```
   pip install .[dev]
```

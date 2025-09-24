# Colocalization Data Import Pipeline (DuckDB)

This guide walks through importing filtered colocalization data into a
DuckDB database, enriching it with parsed and cleaned fields for
analysis.  Instructions for loading data to the previous version
can be found [here](README.v1.md).

## Prerequisites

Ensure the following tools are available:

- [DuckDB](https://duckdb.org/)
- Bash shell
- Compressed TSV input files
- mysql client

Assuming you're using Linux and using the mysql client:

1. **Configure your MySQL credentials:**
   - Edit (or create) your `~/.my.cnf` file.
   - Add a section called `[clientprod]` with your MySQL credentials. For example:
```ini
# place in ~/.my.cnf
     [clientprod]
     user = your_mysql_user
     password = your_mysql_password
     host = your_mysql_host
     port = your_mysql_port
     database = your_mysql_database
 ```

2. **Export MySQL settings as environment variables:**
   Set the following environment variables using your credentials:

```bash
# update to reflect your environment
   export MYSQL_USER=your mysql user
   export MYSQL_PASSWORD=your mysql password
   export MYSQL_HOST=your mysql host
   export MYSQL_PORT=your mysql port
   export MYSQL_DATABASE=your mysql database
```
## Input Files

  This section should change with every data load
  **Update this to reflect your environment**

- environment settings
- colocalization results
- credible sets file

```bash
export TABLE_VERSION=v3
export GROUP_SUFFIX=prod
export GS_COLOC_DATA_PATH=gs://r13-data-green/coloc_susie/release/colocQC.tsv.gz
export GS_CREDSET_DATA_PATH=gs://r13-data-green/coloc_susie/release/coloc.credsets.tsv.gz
```

  Localize files to be loaded

```bash
export WORK_DIRECTORY="/tmp/$TABLE_VERSION"
mkdir -p $WORK_DIRECTORY
export COLOC_DATA_PATH=$WORK_DIRECTORY/`basename $GS_COLOC_DATA_PATH`
export CREDSET_DATA_PATH=$WORK_DIRECTORY/`basename $GS_CREDSET_DATA_PATH`
[ -f "$COLOC_DATA_PATH" ]   && echo "using cache ... $COLOC_DATA_PATH"   || gsutil cp "$GS_COLOC_DATA_PATH" "$COLOC_DATA_PATH"
[ -f "$CREDSET_DATA_PATH" ] && echo "using cache ... $CREDSET_DATA_PATH" || gsutil cp "$GS_CREDSET_DATA_PATH" "$CREDSET_DATA_PATH"
```

   Check file headers
   
```bash
echo "COLOC_DATA_PATH : $COLOC_DATA_PATH"
zcat $COLOC_DATA_PATH | head -n 1
echo "CREDSET_DATA_PATH : $CREDSET_DATA_PATH"
zcat $CREDSET_DATA_PATH | head -n 1
```



## Cloud settings

If you are working in a GCP environment, set these variables to reflect
your environment.

```bash
export GS_PATH="gs://r13-data-green/pheweb/coloc_susie"
export INSTANCE_NAME="production-releases-pheweb-database"
```

## Setup

Define the environment variables:

```bash
export DB_PATH="${WORK_DIRECTORY}/colocalization.db"
export DUCKDB_CMD="env COLOC_DATA_PATH=${COLOC_DATA_PATH} CREDSET_DATA_PATH=${CREDSET_DATA_PATH} duckdb $DB_PATH"
export CONNECTION_STRING="user=${MYSQL_USER} port=${MYSQL_PORT} database=${MYSQL_DATABASE} password=${MYSQL_PASSWORD} host=${MYSQL_HOST}"
echo $CONNECTION_STRING
echo $GROUP_SUFFIX
```

Make sure the DuckDB database has the MySQL extension installed.

```bash
$DUCKDB_CMD <<EOF
INSTALL mysql;
EOF
```

Check duckdb setup

```bash
$DUCKDB_CMD <<EOF
ATTACH '${CONNECTION_STRING}' AS mysqldb (TYPE mysql);
SELECT 1 FROM mysqldb.information_schema.tables LIMIT 1;
EOF
```
Check mysql setup
```bash
mysql --defaults-group-suffix=${GROUP_SUFFIX} <<EOF
select 1
EOF
```
## Import Data into DuckDB

This command creates a duckdb table colocalization from the compressed TSV
file with additional cleaned columns.

```bash
$DUCKDB_CMD <<EOF
DROP TABLE IF EXISTS colocalization;

CREATE TABLE colocalization AS
        SELECT
            row_number() OVER () AS colocalization_id,

            dataset1,
	        REPLACE(list_extract(split(dataset1, '--'), 1), '_', ' ') AS dataset1_label,

            dataset2,
	        REPLACE(list_extract(split(dataset2, '--'), 1), '_', ' ') AS dataset2_label,

            trait1,
            trait2,

	    region1,

            CASE WHEN regexp_extract(region1, 'chr(\w+):-?(\d+)-(\d+)', 1) = 'X' THEN 23
                WHEN regexp_extract(region1, 'chr(\w+):-?(\d+)-(\d+)', 1) = 'Y' THEN 24
                WHEN regexp_extract(region1, 'chr(\w+):-?(\d+)-(\d+)', 1) = 'MT' THEN 25
                ELSE CAST(regexp_extract(region1, 'chr(\w+):-?(\d+)-(\d+)', 1) AS TINYINT)
            END AS region1_chromosome,

            CAST(regexp_extract(region1, 'chr(\w+):-?(\d+)-(\d+)', 2) AS BIGINT) AS region1_start,
            CAST(regexp_extract(region1, 'chr(\w+):-?(\d+)-(\d+)', 3) AS BIGINT) AS region1_end,

	    region2,

            CASE WHEN regexp_extract(region2, 'chr(\w+):-?(\d+)-(\d+)', 1) = 'X' THEN 23
                WHEN regexp_extract(region2, 'chr(\w+):-?(\d+)-(\d+)', 1) = 'Y' THEN 24
                WHEN regexp_extract(region2, 'chr(\w+):-?(\d+)-(\d+)', 1) = 'MT' THEN 25
                ELSE CAST(regexp_extract(region2, 'chr(\w+):-?(\d+)-(\d+)', 1) AS TINYINT)
            END AS region2_chromosome,

            CAST(regexp_extract(region2, 'chr(\w+):-?(\d+)-(\d+)', 2) AS BIGINT) AS region2_start,
            CAST(regexp_extract(region2, 'chr(\w+):-?(\d+)-(\d+)', 3) AS BIGINT) AS region2_end,

            cs1,
            cs2,

            nsnps,

	    hit1,

	    CASE WHEN split_part(hit1_info, ',', 1) == 'NA' THEN null
                 ELSE CAST(split_part(hit1_info, ',', 1) AS DOUBLE)
            END AS hit1_beta,
	    CASE WHEN split_part(hit1_info, ',', 2) == 'NA' THEN null
                 ELSE CAST(split_part(hit1_info, ',', 2) AS DOUBLE)
            END AS hit1_pvalue,

	    hit2,

	    CASE WHEN hit2_info = 'NA' OR split_part(hit2_info, ',', 1) == 'NA' THEN null
                 ELSE CAST(split_part(hit2_info, ',', 1) AS DOUBLE)
            END AS hit2_beta,
	    CASE WHEN hit2_info = 'NA' OR split_part(hit2_info, ',', 2) == 'NA' OR split_part(hit2_info, ',', 2) == '' THEN null
                  ELSE CAST(split_part(hit2_info, ',', 2) AS DOUBLE)
            END AS hit2_pvalue,

	    "PP.H0.abf" AS PPH0abf,
	    "PP.H1.abf" AS PPH1abf,
	    "PP.H2.abf" AS PPH2abf,
	    "PP.H3.abf" AS PPH3abf,
        "PP.H4.abf" AS PPH4abf,

	    low_purity1,
            low_purity2,

	    nsnps1,
	    nsnps2,

	    cs1_log10bf,
	    cs2_log10bf,

            CASE WHEN clpp == 'NA' THEN null
                ELSE CAST(clpp AS DOUBLE)
            END AS clpp,

            CASE WHEN clpa == 'NA' THEN null
                ELSE CAST(clpa AS DOUBLE)
            END AS clpa,

	    cs1_size,
        cs2_size,

        cs_overlap,
	    topInOverlap,

	    probmass_1,
	    probmass_2,

	    hit1_info,
	    hit2_info,

	    colocRes

        FROM read_csv(
            getenv('COLOC_DATA_PATH'),
            delim='\t',
            sample_size=-1
        );
EOF
```

Parse and aggregate variant-level information from credible set data
into a structured JSON array per `(dataset, region, trait, cs)`
combination. It creates a new DuckDB table named
`colocalization_variants`.

```bash
$DUCKDB_CMD <<EOF
DROP TABLE IF EXISTS colocalization_variants;

CREATE TABLE colocalization_variants AS
SELECT
    -- Parse chromosome from region string
    CASE WHEN regexp_extract(region, 'chr(\w+):-?(\d+)-(\d+)', 1) = 'X' THEN 23
         WHEN regexp_extract(region, 'chr(\w+):-?(\d+)-(\d+)', 1) = 'Y' THEN 24
         WHEN regexp_extract(region, 'chr(\w+):-?(\d+)-(\d+)', 1) = 'MT' THEN 25
         ELSE CAST(regexp_extract(region, 'chr(\w+):-?(\d+)-(\d+)', 1) AS TINYINT)
    END AS region_chromosome,

    -- Parse start and end coordinates
    CAST(regexp_extract(region, 'chr(\w+):-?(\d+)-(\d+)', 2) AS BIGINT) AS region_start,
    CAST(regexp_extract(region, 'chr(\w+):-?(\d+)-(\d+)', 3) AS BIGINT) AS region_end,

    dataset,
    trait,
	cs::TINYINT AS cs,
    -- Aggregate variant-level data into a JSON array
    to_json(ARRAY_AGG(JSON_OBJECT(
        'rsid', rsid,
        'position', CAST(REGEXP_EXTRACT(rsid, 'chr(\w+)_([0-9]+)', 2) AS UBIGINT),
        'cs', CAST(cs AS TINYINT),
        'low_purity',
            CASE WHEN low_purity = 0 THEN FALSE
                 WHEN low_purity = 1 THEN TRUE
                 ELSE ERROR('Invalid value in col: must be 0 or 1')
            END,
        'p',    CASE WHEN p == 'NA'    THEN null ELSE CAST(p    AS FLOAT) END,
        'beta', CASE WHEN beta == 'NA' THEN null ELSE CAST(beta AS FLOAT) END,
        'se',   CASE WHEN se == 'NA'   THEN null ELSE CAST(se   AS FLOAT) END,
        'cs_specific_prob', CAST(cs_specific_prob AS FLOAT)
    ))) AS variants

FROM read_csv('${CREDSET_DATA_PATH}',
              delim='\t',
              sample_size=-1)

GROUP BY dataset, region, trait, cs;
EOF
```

## Step 3: Export Data from DuckDB to files

Transfer the processed colocalization data from the DuckDB database to
a tsv file.



```bash
$DUCKDB_CMD <<EOF
CREATE TABLE colocalization.colocalization_stage AS
SELECT
  colocalization_id,
  dataset1, dataset1_label,
  dataset2, dataset2_label,
  trait1,
  trait2,
  CASE WHEN region1_chromosome != region2_chromosome THEN NULL
       ELSE region1_chromosome
  END AS region_chromosome,
  CASE
    WHEN region1_chromosome = region2_chromosome AND region1_end >= region2_start AND region2_end >= region1_start
      THEN LEAST(region1_start, region2_start)
    ELSE NULL
  END AS region_start,
  CASE
    WHEN region1_chromosome = region2_chromosome AND region1_end >= region2_start AND region2_end >= region1_start
      THEN GREATEST(region1_end, region2_end)
    ELSE NULL
  END AS region_end,
  region1, region1_chromosome, region1_start, region1_end,
  region2, region2_chromosome, region2_start, region2_end,
  cs1,
  cs2,
  nsnps,
  hit1,
  hit2,
  PPH0abf,
  PPH1abf,
  PPH2abf,
  PPH3abf,
  PPH4abf,
  low_purity1,
  low_purity2,
  nsnps1,
  nsnps2,
  CASE
    WHEN cs1_log10bf = 'inf'::DOUBLE OR cs1_log10bf = '-inf'::DOUBLE THEN NULL
    ELSE cs1_log10bf
  END AS cs1_log10bf,
  (cs1_log10bf = 'inf'::DOUBLE OR cs1_log10bf = '-inf'::DOUBLE) AS cs1_log10bf_is_infinite,
  CASE
    WHEN cs2_log10bf = 'inf'::DOUBLE OR cs2_log10bf = '-inf'::DOUBLE THEN NULL
    ELSE cs2_log10bf
  END AS cs2_log10bf,
  (cs2_log10bf = 'inf'::DOUBLE OR cs2_log10bf = '-inf'::DOUBLE) AS cs2_log10bf_is_infinite,
  clpp,
  clpa,
  cs1_size,
  cs2_size,
  cs_overlap,
  topInOverlap,
  probmass_1,
  probmass_2,
  hit1_info,
  hit2_info,
  hit1_beta,
  hit1_pvalue,
  hit2_beta,
  hit2_pvalue,
  colocRes
FROM colocalization.colocalization;

COPY(SELECT 
  colocalization_id,
  dataset1, dataset1_label,
  dataset2, dataset2_label,
  trait1, trait2,
  region_chromosome, region_start, region_end,
  region1, region1_chromosome, region1_start, region1_end,
  region2, region2_chromosome, region2_start, region2_end,
  cs1, cs2,
  nsnps,
  hit1, hit2,
  PPH0abf, PPH1abf, PPH2abf, PPH3abf, PPH4abf,
  low_purity1, low_purity2,
  nsnps1, nsnps2,
  cs1_log10bf, cs1_log10bf_is_infinite,
  cs2_log10bf, cs2_log10bf_is_infinite,
  clpp, clpa,
  cs1_size, cs2_size,
  cs_overlap,
  topInOverlap,
  probmass_1, probmass_2,
  hit1_info, hit2_info,
  hit1_beta, hit1_pvalue,
  hit2_beta, hit2_pvalue,
  colocRes
from colocalization.colocalization_stage) 
TO '${WORK_DIRECTORY}/colocalization_${TABLE_VERSION}.tsv.gz' (FORMAT 'csv', DELIMITER E'\t', HEADER TRUE, COMPRESSION 'gzip');
EOF

if [ -n "$GS_PATH" ]; then
  cat "${WORK_DIRECTORY}/colocalization_${TABLE_VERSION}.tsv.gz" | zcat | sed '1d' | gzip --best | gsutil cp - "${GS_PATH}/colocalization_${TABLE_VERSION}.tsv.gz"
fi
```

This step exports `colocalization_variants` data from DuckDB to tsv.

```bash
$DUCKDB_CMD <<EOF
CREATE TABLE colocalization.colocalization_variants_stage AS
SELECT
  region_chromosome, region_start, region_end,
  cs,
  dataset,
  trait,
  variants
FROM colocalization.colocalization_variants;

COPY(SELECT 
  region_chromosome, region_start, region_end,
  cs,
  dataset,
  trait,
  variants
from colocalization.colocalization_variants_stage) 
TO '${WORK_DIRECTORY}/colocalization_variants_${TABLE_VERSION}.tsv.gz' 
(FORMAT 'csv', DELIMITER E'\t', HEADER TRUE, COMPRESSION 'gzip');
EOF

if [ -n "$GS_PATH" ]; then
  cat "${WORK_DIRECTORY}/colocalization_variants_${TABLE_VERSION}.tsv.gz" | zcat | sed '1d' | gzip --best | gsutil cp - "${GS_PATH}/colocalization_variants_${TABLE_VERSION}.tsv.gz"
fi
```

## Step 4: Create MySQL Table

This step creates the `colocalization` table in a MySQL database using
the `${GROUP_SUFFIX}` configuration group. The table schema is designed to mirror
the structure of the DuckDB version, with types adjusted for MySQL
compatibility.

Run the following command:

```bash
mysql --defaults-group-suffix=${GROUP_SUFFIX} <<EOF
DROP TABLE IF EXISTS colocalization_${TABLE_VERSION};

CREATE TABLE colocalization_${TABLE_VERSION} (
  colocalization_id             INTEGER,

  dataset1           VARCHAR(100)  NULL,
  dataset1_label     VARCHAR(100)  NULL,
  dataset2           VARCHAR(100)  NULL,
  dataset2_label     VARCHAR(100)  NULL,

  trait1             VARCHAR(100)  NULL,
  trait2             VARCHAR(100)  NULL,

  region_chromosome         TINYINT       NULL,
  region_start              BIGINT        NULL,
  region_end                BIGINT        NULL,

  region1            VARCHAR(100)  NULL,
  region1_chromosome TINYINT       NULL,
  region1_start      BIGINT        NULL,
  region1_end        BIGINT        NULL,

  region2            VARCHAR(100)  NULL,
  region2_chromosome TINYINT       NULL,
  region2_start      BIGINT        NULL,
  region2_end        BIGINT        NULL,

  cs1                BIGINT        NULL,
  cs2                BIGINT        NULL,

  nsnps              BIGINT        NULL,

  hit1               VARCHAR(500)  NULL,
  hit2               VARCHAR(500)  NULL,

  PPH0abf            DOUBLE        NULL,
  PPH1abf            DOUBLE        NULL,
  PPH2abf            DOUBLE        NULL,
  PPH3abf            DOUBLE        NULL,
  PPH4abf            DOUBLE        NULL,

  low_purity1        BIGINT        NULL,
  low_purity2        BIGINT        NULL,

  nsnps1             BIGINT        NULL,
  nsnps2             BIGINT        NULL,

  cs1_log10bf        DOUBLE        NULL,
  cs1_log10bf_is_infinite BOOLEAN,
  cs2_log10bf        DOUBLE,
  cs2_log10bf_is_infinite BOOLEAN,

  clpp               DOUBLE,
  clpa               DOUBLE,

  cs1_size           BIGINT,
  cs2_size           BIGINT,

  cs_overlap         BIGINT,
  topInOverlap       VARCHAR(100),

  probmass_1         DOUBLE,
  probmass_2         DOUBLE,

  hit1_info          VARCHAR(100),
  hit2_info          VARCHAR(100),

  hit1_beta          DOUBLE,
  hit1_pvalue        DOUBLE,

  hit2_beta          DOUBLE,
  hit2_pvalue        DOUBLE,

  colocRes           VARCHAR(500)  NULL
);
EOF
```

Define the table in MySQL for storing aggregated variant-level data as
JSON. Each row corresponds to a unique `(dataset, region, trait, cs)`
combination and includes a JSON array of variant details.

Run the following command to create the table:

```bash
mysql --defaults-group-suffix=${GROUP_SUFFIX} <<EOF
DROP TABLE IF EXISTS colocalization_variants_${TABLE_VERSION};

CREATE TABLE colocalization_variants_${TABLE_VERSION} (
    region_chromosome TINYINT NOT NULL,
    region_start BIGINT NOT NULL,
    region_end BIGINT NOT NULL,
    cs TINYINT NOT NULL,
    dataset VARCHAR(255) NOT NULL,
    trait VARCHAR(255) NOT NULL,
    variants JSON NOT NULL
);
EOF
```
## Step 5: Import data to MySQL

### Import Colocalization Data
This step transfers the processed colocalization data from the DuckDB
database to the MySQL `colocalization` table created earlier.

There are three options for the next step: **MySQL LOAD**, **DuckDB import**, and **gcloud SQL import**. Choose based on your setup and data size:

- **DuckDB import**  
  Development: Use if your dataset is small (~200 MB) and the MySQL connection is fast and stable.

- **MySQL LOAD**  
  Local : Use for large datasets (>200 MB) on **non-GCP MySQL** servers.
  
- **gcloud SQL import**  
  Use for large datasets (>200 MB) on **Google Cloud SQL**.


### Duckdb import
```bash
# import using duckdb development
$DUCKDB_CMD <<EOF
INSTALL mysql;
-- Connect to the MySQL database using credentials
ATTACH '${CONNECTION_STRING}' AS mysqldb (TYPE mysql);

-- Export the colocalization table from DuckDB to MySQL
INSERT INTO mysqldb.${MYSQL_DATABASE}.colocalization_${TABLE_VERSION}
SELECT * FROM colocalization.colocalization_stage;
EOF
```

### MySQL Load

```bash
# import using mysql local database
gunzip -c ${WORK_DIRECTORY}/colocalization_${TABLE_VERSION}.tsv.gz | mysql --defaults-group-suffix=${GROUP_SUFFIX} --local-infile=1  -e "
      LOAD DATA LOCAL INFILE '/dev/stdin'
      INTO TABLE colocalization_${TABLE_VERSION}
      FIELDS TERMINATED BY '\t'
      OPTIONALLY ENCLOSED BY '\"'
      LINES TERMINATED BY '\n'
      IGNORE 1 LINES;
"
```
### Gcloud SQL Import

```bash
OP=$(gcloud sql import csv ${INSTANCE_NAME} \
  "${GS_PATH}/colocalization_${TABLE_VERSION}.tsv.gz" \
  --database=${MYSQL_DATABASE} \
  --table="colocalization_${TABLE_VERSION}" \
  --escape=5C --fields-terminated-by=09  --quote=22 \
  --async --quiet)
echo "Started op: $OP"
echo loading "${GS_PATH}/colocalization_${TABLE_VERSION}.tsv.gz" to database "${MYSQL_DATABASE}"
```

## Step 6: Export `colocalization_variants` to MySQL and Create Indexes

This step transfers the aggregated `colocalization_variants` data from
DuckDB to MySQL, and creates indexes on both DuckDB and MySQL tables
to support fast region-based lookups.

### Command

Run the following:


```bash
$DUCKDB_CMD <<EOF
INSTALL mysql;
-- Connect to the MySQL database using credentials
ATTACH '${CONNECTION_STRING}' AS mysqldb (TYPE mysql);

-- Export the variants table from DuckDB to MySQL
INSERT INTO mysqldb.${MYSQL_DATABASE}.colocalization_variants_${TABLE_VERSION}
SELECT * FROM colocalization.colocalization_variants_stage;
EOF
```




## Step 7: Create Index and Views in MySQL

This step improves query performance on colocalization data and
defines useful SQL views pheweb. It includes the creation of an
index for region queries and multiple views for phenotypes, regions,
and enriched variant joins.

### Indexes


Create the indexes for the mysql database for region-based lookups

```bash
mysql --defaults-group-suffix=${GROUP_SUFFIX} <<EOF
CREATE INDEX idx_colocalization_variants_${TABLE_VERSION}
    ON colocalization_variants_${TABLE_VERSION}(region_chromosome, region_start, region_end, dataset, trait, cs);

CREATE INDEX idx_colocalization_region1_${TABLE_VERSION}
    ON colocalization_${TABLE_VERSION}(region1_chromosome, region1_start, region1_end, dataset1, trait1, cs1);

CREATE INDEX idx_colocalization_region2_${TABLE_VERSION}
    ON colocalization_${TABLE_VERSION}(region2_chromosome, region2_start, region2_end, dataset2, trait2, cs2);
EOF
```

### Views

Create the views for pheweb to query:

```
mysql --defaults-group-suffix=${GROUP_SUFFIX} <<EOF
drop view if exists colocalization_phenotype_${TABLE_VERSION};
create view colocalization_phenotype_${TABLE_VERSION} as
select distinct trait1 as phenotype from colocalization_${TABLE_VERSION};

drop view if exists colocalization_region_${TABLE_VERSION};
create view colocalization_region_${TABLE_VERSION} as
SELECT c.dataset1_label AS dataset1,
       c.dataset2_label AS dataset2,
       c.region_chromosome,
       c.region_start,
       c.region_end,
       c.trait1,
       c.trait2,
       c.hit1 AS locus_id1,
       c.hit2 AS locus_id2,
       cs1_size AS cs_size_1,
       cs2_size AS cs_size_2,
       hit1_beta AS beta1,
       hit1_pvalue AS pval1,
       hit2_beta AS beta2,
       hit2_pvalue AS pval2,
       PPH4abf AS pp_h4_abf,
       c.clpp AS clpp,
       c.clpa AS clpa,
       c.colocalization_id,
       c.trait1 as phenotype,
       v1.variants AS variant1 ,
       v2.variants AS variant2
FROM colocalization_${TABLE_VERSION} AS c
LEFT JOIN colocalization_variants_${TABLE_VERSION} AS v1
    ON c.region1_chromosome = v1.region_chromosome
   AND c.region1_start = v1.region_start
   AND c.region1_end = v1.region_end
   AND c.dataset1 = v1.dataset
   AND c.trait1 = v1.trait
   AND c.cs1 = v1.cs
LEFT JOIN colocalization_variants_${TABLE_VERSION} AS v2
    ON c.region2_chromosome = v2.region_chromosome
   AND c.region2_start = v2.region_start
   AND c.region2_end = v2.region_end
   AND c.dataset2 = v2.dataset
   AND c.trait2 = v2.trait
   AND c.cs2 = v2.cs
   ;

EOF
```


## Step 7 : Checks


Check the outputs of these queries to check
the tables.

```
mysql --defaults-group-suffix=${GROUP_SUFFIX} <<EOF
select min(beta1) min_beta1, avg(beta1) avg_beta1, max(beta1) max_beta1, 
       min(beta2) min_beta2, avg(beta2) avg_beta2, max(beta1) max_beta2,
       avg(pval1) avg_pval1, avg(pval2) avg_pval2 from colocalization_region_${TABLE_VERSION};
select count(distinct dataset1) count_dataset1, count(distinct dataset2) count_dataset2 from colocalization_region_${TABLE_VERSION};
EOF
```

## Step 7: Update PheWeb Configuration for Colocalization V2

To enable the updated colocalization tables in your PheWeb deployment,
update the configuration to include the `ColocalizationV2DAO` stanza.

### Configuration Snippet

Modify your PheWeb backend configuration (`config.py`) to include the
following, with the table names adjusted to match your environment:

```python
# place in config.py
database_conf = (
{ "colocalization": {
    "ColocalizationV2DAO": {
      "authentication_file": "/etc/gcp/mysql.conf",
      "parameters": {
        "phenotype_table": "colocalization_phenotype_${TABLE_VERSION}",
        "region_table": "colocalization_region_${TABLE_VERSION}",
        "region_summary_table": "colocalization_region_${TABLE_VERSION}",
        "colocalization_table": "colocalization_region_${TABLE_VERSION}",
        "region_summary_columns": {
          "count": "count(*)",
          "unique_phenotype2": "count(distinct trait2)",
          "unique_tissue2": "count(distinct null)"
        }
      }
    }
  }
},)
```


### Tearing down

To clean up the resources, first reconfigure the PheWeb instances to
stop using the colocalization tables. Then run the following SQL to
drop the related tables and views.

```
mysql --defaults-group-suffix=${GROUP_SUFFIX} <<EOF
drop table if exists colocalization_${TABLE_VERSION};
drop table if exists colocalization_variants_${TABLE_VERSION};
drop view  if exists colocalization_phenotype_${TABLE_VERSION};
drop view  if exists colocalization_region_${TABLE_VERSION};
EOF

rm ${DB_PATH}

```

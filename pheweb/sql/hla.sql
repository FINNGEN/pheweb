CREATE TABLE hla (
  id int NOT NULL AUTO_INCREMENT,
  phenocode varchar(255) NOT NULL,
  chrom int NOT NULL,
  pos int NOT NULL,
  ref varchar(255) NOT NULL,
  alt varchar(255) NOT NULL,
  pval double NOT NULL,
  mlogp double NOT NULL,
  beta double NOT NULL,
  sebeta double NOT NULL,
  af_alt double NOT NULL,
  af_alt_cases double DEFAULT NULL,
  af_alt_controls double DEFAULT NULL,
  PRIMARY KEY (id),
  INDEX phenocode_index (phenocode),
  INDEX variant_index (alt)
)
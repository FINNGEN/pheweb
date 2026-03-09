CREATE TABLE hla (
  id int NOT NULL AUTO_INCREMENT,
  phenocode varchar(255) NOT NULL,
  chrom int DEFAULT NULL,
  pos bigint DEFAULT NULL,
  ref varchar(255) DEFAULT NULL,
  alt varchar(255) DEFAULT NULL,
  pval double DEFAULT NULL,
  mlogp double DEFAULT NULL,
  beta double DEFAULT NULL,
  sebeta double DEFAULT NULL,
  af_alt double DEFAULT NULL,
  af_alt_cases double DEFAULT NULL,
  af_alt_controls double DEFAULT NULL,
  PRIMARY KEY (id),
  INDEX phenocode_index (phenocode),
  INDEX variant_index (alt)
)
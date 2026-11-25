const hlaConfig = {
  "title": "HLA association results",
  "help" : `Phewas results of classical HLA alleles analysed with Regenie in same way as the basic FinnGen GWAS results. HLA allele imputation in FinnGen is implemented using R library <a href="https://bioconductor.org/packages/release/bioc/html/HIBAG.html" target="_blank" rel="noopener noreferrer">HIBAG</a> with imputation models trained on Finnish individuals (<a href="https://github.com/FRCBS/HLA-imputation" target="_blank" rel="noopener noreferrer">https://github.com/FRCBS/HLA-imputation</a>).
  
  The Finnish reference data have been genotyped at clinical grade accuracy at 4-digit (i.e. amino acid) level resolution for the HLA genes HLA-A, B, C, DPB1, DQA1, DQB1, DRB1, DRB3, DRB4 and DRB5. HLA imputation of FinnGen data is based on a set of SNPs directly genotyped on the FinnGen array, however, this set is extracted from SNP-imputed data so that approximately the same set of SNPs should be present in all samples regardless of their original genotyping platform.
  
  <strong>NOTE: significant result here does not necessarily mean that the allele is causal but result need to be interpreted together with the GWAS association results from regular imputed GWAS results in the region.</strong>`
}

export default hlaConfig;

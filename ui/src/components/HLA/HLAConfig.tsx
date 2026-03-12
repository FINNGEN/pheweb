const hlaConfig = {
  "title": "HLA association results",
  "help" : "Phewas results of classical HLA alleles analysed with Regenie in same way as the basic FinnGen GWAS results. HLA</br> allele imputation in FinnGen is implemented using R library HIBAG with imputation models trained on Finnish individuals.</br> The Finnish reference data have been genotyped at clinical grade accuracy at 4-digit (i.e. amino acid) level resolution </br>for the HLA genes HLA-A, B, C, DPB1, DQA1, DQB1, DRB1, DRB3, DRB4 and DRB5. HLA imputation of FinnGen data is </br>based on a set of SNPs directly genotyped on the FinnGen array, however, this set is extracted from SNP-imputed data</br> so that approximately the same set of SNPs should be present in all samples regardless of their original genotyping</br> platform. </br> <strong>NOTE: significant result here does not necessarily mean that the allele is causal but result need to be interpreted</br> together with the GWAS association results from regular imputed GWAS results in the region.</strong>"
}

export default hlaConfig;

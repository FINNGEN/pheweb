import { TableColumnConfiguration } from "../../common/tableColumn";

export namespace Gene {

  export interface DrugsConfiguration {
    banner?: string
    tableColumns? : TableColumnConfiguration<GeneDrugs.Row>
  }

  export interface GenePhenotypeConfiguration {
    banner?: string
    footer?:string
    tableColumns? : TableColumnConfiguration<GenePhenotypes.ViewRow>
  }

  export interface GeneLossOfFunctionConfiguration {
    banner?: string
    empty?: string
    tableColumns? : TableColumnConfiguration<LossOfFunction.ViewRow>
  }

  export interface GeneFunctionalVariants {
    banner?: string
    empty? : string
    tableColumns? : TableColumnConfiguration<FunctionalVariants.ViewRow>
  }

  export interface Configuration {
    banner?: string
    phenotype? : GenePhenotypeConfiguration
    lossOfFunction? : GeneLossOfFunctionConfiguration
    functionalVariants? : GeneFunctionalVariants
    drugs? : DrugsConfiguration
  }
}
export namespace FunctionalVariants {

  export interface ViewRow {
    rsids : string ,
    alt : string ,
    chrom : number,
    pos : number ,
    ref : string ,
    most_severe : string ,
    info : string ,
    maf : number
    fin_enrichment : string
    significant_phenos: SignificantPheno[]
  }
  export type Data = Row[]

  export interface Row {
    rsids:              string
    significant_phenos: SignificantPheno[]
    var:                Var
  }

  export interface SignificantPheno {
    beta:             number
    category:         string
    category_index:   number | null
    maf:              number
    maf_case:         number
    maf_control:      number
    matching_results: {}
    mlogp:            number
    n_case:           number
    n_control:        number
    n_sample:         'NA' | number
    phenocode:        string
    phenostring:      string
    pval:             number
  }

  export interface Var {
    alt:        string
    annotation: Annotation
    chr:        number
    pos:        number
    ref:        string
    varid:      string
  }

  export interface Annotation {
    annot:        { [key: string]: string }
    nearest_gene: string
    rsids:        string
    gnomad?:      { [key: string]: string }
  }
}
export namespace LossOfFunction {
  export type Data = Row[]

  export  interface ViewRow {
    phenostring : string
    phenocode : string

    variants : string
    pval:         number;
    beta:            number;

    alt_count_cases: number;
    alt_count_ctrls: number;

    ref_count_cases: number;
    ref_count_ctrls: number;
  }

  export interface Row {
    gene_data: GeneData;
  }

  export interface GeneData {
    ac:              number;
    af:              number;
    alt_count_cases: number;
    alt_count_ctrls: number;
    beta:            string;
    gene:            string;
    id:              number;
    n:               number;
    p_value:         number;
    pheno:           string;
    phenostring:     string;
    ref_count_cases: number;
    ref_count_ctrls: number;
    rel:             number;
    se:              number;
    variants:        string;
  }

}
export namespace GeneDrugs {
  export type Data = Row[]
  export type View = {}

  export interface Row {
    approvedName?:              string;
    diseaseName?:               string;
    drugId?:                    string;
    drugType?:                  string;
    maximumClinicalTrialPhase?: number;
    mechanismOfAction:         string;
    phase:                     number;
    prefName:                  string;
    targetClass:               string[];
    EFOInfo?:                  string;
  }
}
export namespace GenePhenotypes {

  export interface ViewRow {
    readonly num_cases : number
    readonly beta : number
    readonly rsids: string
    readonly fin_enrichment: string
    readonly mlogp : number
    readonly phenostring : string
    readonly phenocode : string
    readonly category : string
    readonly pval : number
    readonly chrom : number
    readonly pos : number
    readonly ref : string
    readonly alt : string
    readonly gene : string
  }

  export interface  Region {
    readonly chrom : number
    readonly start : number
    readonly end : number
  }

  export type Data = {
    readonly region : Region
    readonly phenotypes : Phenotype[]
  }

  export interface Phenotype {
    readonly assoc:   Association
    readonly pheno:   Phenotype
    readonly variant: Variant
  }

  export interface Association {
    readonly beta:             number;
    readonly category:         string;
    readonly category_index:   number | null;
    readonly maf:              number;
    readonly maf_case:         number;
    readonly maf_control:      number;
    readonly matching_results: {};
    readonly mlogp:            number;
    readonly n_case:           number;
    readonly n_control:        number;
    readonly n_sample:         number | "NA";
    readonly phenocode:        string;
    readonly phenostring:      string;
    readonly pval:             number;
  }


  export interface Phenotype {
    readonly assoc_files:             string[];
    readonly category:                string;
    readonly category_index?:         number;
    readonly gc_lambda:               { [key: string]: number };
    readonly num_cases:               number;
    readonly num_cases_prev:          "NA" | number;
    readonly num_controls:            number;
    readonly num_gw_significant:      number;
    readonly num_gw_significant_prev: "NA" | number;
    readonly phenocode:               string;
    readonly phenostring:             string;
  }

  export interface Variant {
    readonly alt:        string;
    readonly annotation: Annotation;
    readonly chr:        number;
    readonly pos:        number;
    readonly ref:        string;
    readonly varid:      string;
  }

  export interface Annotation {
    readonly gnomad?:       { [key: string]: (string | number) };
    readonly nearest_gene: string;
    readonly rsids?:       string;
  }


}
export namespace MyGene {
  export interface Data {
    took: number;
    total: number;
    max_score: number;
    hits: Hit[];
  }

  export interface Hit {
    MIM: string;
    _id: string;
    _score: number;
    ensembl: Ensembl;
    entrezgene: string;
    name: string;
    summary: string;
    symbol: string;
  }

  export interface Ensembl {
    gene: string;
  }
}
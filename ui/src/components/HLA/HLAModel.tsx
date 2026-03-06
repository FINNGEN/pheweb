export namespace HLAModel {
    export type Data = Row[]

    export interface Row {
        phenocode: string
        number_chrom: number
        pos: number
        ref: string
        gene: string
        alt: string
        pval: number
        mlogp: number
        beta: number
        sebeta: number
        af_alt: number
        af_alt_cases: number
        af_alt_controls: number
    }
}

export default HLAModel;

export interface HLAConfiguration {}

export interface PhenotypeSearchResult {
    phenocode: string
}
export interface GeneSearchResult {
    gene: string
}
export interface VariantSearchResult {
    alt: string
}

export type SearchResult = PhenotypeSearchResult | GeneSearchResult | VariantSearchResult
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

export namespace AutoCompleteModel {
    type PhenotypeSearchResultRow = {
        phenocode: string
    }
    type GeneSearchResultRow = {
        gene: string
    }
    type VariantSearchResultRow = {
        alt: string
    }
    export type Row = PhenotypeSearchResultRow | GeneSearchResultRow | VariantSearchResultRow
    export type Data = Row[]
}
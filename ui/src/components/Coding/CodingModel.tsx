export namespace CodingModel {
    export interface Data {
        results: Row[]
    }

    export interface Row {
        phenocode: string
        phenostring: string
        variant: string
        af: number | null
        info: number | null
        rsid: string | null
        most_severe: string | null
        gene_most_severe: string | null
        enrichment: number | 'inf' | null
        mlogp_add: number | null
        beta_add: number | null
        sebeta_add: number | null
        mlogp_chip_add: number | null
        beta_chip_add: number | null
        sebeta_chip_add: number | null
        mlogp_chip_rec: number | null
        beta_chip_rec: number | null
        sebeta_chip_rec: number | null
        rec_add: number | null
        possible_explaining_signals: string | null
        is_top_pheno: boolean
    }
}

export default CodingModel;

export const defaultDataset : string = "gnomad_r4";

export interface CodingConfiguration {
  config? : { [key: string]: any };
  dataset? : string;
}

export namespace AutoCompleteModel {
    export type Row = {
        label: string
        value: string
        type: 'phenotype' | 'gene' | 'variant'
    }
    export type Data = Row[]
}
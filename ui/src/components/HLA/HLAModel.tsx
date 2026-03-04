export namespace HLAModel {
    export type Data = Row[]
    
    export interface Row {
        endpoint: string
        number_chrom: number
        pos: number
        ref: string
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
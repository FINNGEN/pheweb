import { get, Handler } from "../../common/commonUtilities";
import { resolveURL } from "../Configuration/configurationModel";
import { HLAModel, SearchResult } from "./HLAModel";

export const getTopHLAResults = (
    sink: (s: HLAModel.Data) => void,
    getURL = get): void => {
    getURL(resolveURL(`/api/v1/hla/top`), sink)
}

export const getByPhenocode = (phenocode: string,
    sink: (s: HLAModel.Data) => void,
    handler: Handler = (url: string) => (e: Error) => console.error(`Loading HLA data for phenocode ${phenocode} ${e.message}`),
    getURL = get): void => {
    const url = resolveURL(`/api/v1/hla/phenocode/${phenocode}`)
    getURL(url, sink, handler)
}

export const getByGene = (gene: string,
    sink: (s: HLAModel.Data) => void,
    handler: Handler = (url: string) => (e: Error) => console.error(`Loading HLA data for gene ${gene} ${e.message}`),
    getURL = get): void => {
    const url = resolveURL(`/api/v1/hla/gene/${gene}`)
    getURL(url, sink, handler)
}
export const getByVariant = (variant: string,
    sink: (s: HLAModel.Data) => void,
    handler: Handler = (url: string) => (e: Error) => console.error(`Loading HLA data for variant ${variant} ${e.message}`),
    getURL = get): void => {
    const url = resolveURL(`/api/v1/hla/variant/${variant}`)
    getURL(url, sink, handler)
}

export const getAutocomplete = (
    sink: (s: SearchResult[]) => void,
    handler: Handler = (url: string) => (e: Error) => console.error(`Loading HLA autocomplete data ${e.message}`),
    getURL = get): void => {
    const url = resolveURL('/api/v1/hla/autocomplete')
    getURL(url, sink, handler)
}
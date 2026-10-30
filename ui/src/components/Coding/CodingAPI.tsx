import { get, Handler } from "../../common/commonUtilities";
import { resolveURL } from "../Configuration/configurationModel";
import { CodingModel, AutoCompleteModel } from "./CodingModel";

type Sink<Datatype> = (s: Datatype) => void

export function getTopResults(sink: Sink<CodingModel.Data>, handler?: Handler): void {
    get(resolveURL('/api/v1/coding/top'), sink, handler)
}

export function getByVariant(variant: string, sink: Sink<CodingModel.Data>, handler?: Handler): void {
    const url = resolveURL(`/api/v1/coding/variant/${variant}`)
    get(url, sink, handler)
}

export function getByGene(gene: string, sink: Sink<CodingModel.Data>, handler?: Handler): void {
    const url = resolveURL(`/api/v1/coding/gene/${gene}`)
    get(url, sink, handler)
}

export function getByPhenocode(phenocode: string, sink: Sink<CodingModel.Data>, handler?: Handler): void {
    const url = resolveURL(`/api/v1/coding/phenocode/${phenocode}`)
    get(url, sink, handler)
}

export const clusterPlotURL = (variant: string): string =>
    resolveURL(`/api/v1/coding/cluster_plot/${variant.replace(/-/g, "_")}`)

export function getAutocomplete(query: string, sink: Sink<AutoCompleteModel.Data>, handler?: Handler): void {
    const url = resolveURL('/api/v1/coding/autocomplete', { query })
    get(url, sink, handler)
}

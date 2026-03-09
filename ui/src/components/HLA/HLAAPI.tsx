import { get, Handler } from "../../common/commonUtilities";
import { resolveURL } from "../Configuration/configurationModel";
import { HLAModel, AutoCompleteModel } from "./HLAModel";

type Sink<Datatype> = (s: Datatype) => void

export function getTopHLAResults(sink: Sink<HLAModel.Data>): void {
    get(resolveURL('/api/v1/hla/top'), sink)
}

export function getByPhenocode(phenocode: string, sink: Sink<HLAModel.Data>): void {
    const url = resolveURL(`/api/v1/hla/phenocode/${phenocode}`)
    get(url, sink)
}

export function getByGene(gene: string, sink: Sink<HLAModel.Data>): void {
    const url = resolveURL(`/api/v1/hla/gene/${gene}`)
    get(url, sink)
}
export function getByVariant(variant: string, sink: Sink<HLAModel.Data>): void {
    const url = resolveURL(`/api/v1/hla/variant/${variant}`)
    get(url, sink)
}

export function getAutocomplete(sink: Sink<AutoCompleteModel.Data>): void {
    const url = resolveURL('/api/v1/hla/autocomplete')
    get(url, sink)
}
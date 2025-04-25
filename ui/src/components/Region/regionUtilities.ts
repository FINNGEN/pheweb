import {Summary} from "./regionModel";
import RegionSummaryType = Summary.RegionSummaryType;
import {Locus} from "../../common/commonModel";

export const regionSummaryTypes =  (regionSummary: Summary.RegionSummary): Summary.RegionSummaryType[] => (Object.keys(countCredibleSetTypes(regionSummary.credible_sets)) as Summary.RegionSummaryType[]);
export const regionTypes =  (region: Summary.Region) => Array.from(new Set(region.region_summary.flatMap(regionSummaryTypes)));

// Use reduce to accumulate counts based on the type value
type SummaryTypeCount = { [key in Summary.RegionSummaryType]: number }
const countCredibleSetTypesReduce = (acc :SummaryTypeCount, item : Summary.CredibleSetSummary<Summary.RegionSummaryType>): Record<Summary.RegionSummaryType, number> => { acc[item.type] = (acc[item.type] || 0) + 1; return acc; }
const countCredibleSetTypes = (credible_sets : Summary.CredibleSetSummary<Summary.RegionSummaryType>[]) : Record<Summary.RegionSummaryType, number> => credible_sets.reduce(countCredibleSetTypesReduce, {} as Record<Summary.RegionSummaryType, number>);
export type CountCredibleSetTypes = { type : RegionSummaryType , count : number }
export const countListCredibleSetTypes = (credible_sets : Summary.CredibleSetSummary<Summary.RegionSummaryType>[]) : CountCredibleSetTypes[] => {
    const transformed : [Summary.RegionSummaryType, number][] = Object.entries(countCredibleSetTypes(credible_sets)).map(([key, value] ) => [key , value] as [Summary.RegionSummaryType, number]);
    transformed.sort(([keyA], [keyB]) => {
        if (keyA < keyB) return -1;  // keyA comes first
        if (keyA > keyB) return 1;   // keyB comes first
        return 0;                    // keys are equal
    });
    return transformed.map(([type , count ])=> ({ type , count }));
}

export const regionLabel = (locus: Locus) => `${locus.chromosome}:${locus.start}-${locus.stop}`;
export const regionURL = (phenocode : string, locus: Locus) => `/region/${phenocode}/${locus.chromosome}:${locus.start}-${locus.stop}`

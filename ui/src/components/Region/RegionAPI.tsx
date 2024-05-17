import { Region, RegionParams } from "./RegionModel";
import { get, Handler } from "../../common/commonUtilities";
import { resolveURL } from "../Configuration/configurationModel";
import { Locus } from "../../common/commonModel";
import { FinemapData } from "./LocusZoom/RegionModel";

/**
 * Given a colocalization parameter
 * return the url to get region
 * metadata
 *
 * @param parameter
 */
export const region_url = (parameter : RegionParams<Locus>) : string =>  `/api/region/${parameter.phenotype}/${parameter.locus.chromosome}:${parameter.locus.start}-${parameter.locus.stop}`

/**
 * Given a parameter return the region matching
 * parameter
 *
 * @param parameter to search
 * @param sink
 * @param getURL
 */
export const getRegion = (parameter: RegionParams<Locus> | undefined,
                          sink: (s: Region) => void,
                          getURL = get) =>
    parameter &&  getURL<Region>(resolveURL(region_url(parameter)),sink);



export const get_finemap_cond_region_url = (region: string, type: string, pheno: string) : string => {
    const chr = region.split(":")[0];
    const start = Number(region.split(":")[1].split("-")[0]);
    const end = Number(region.split(":")[1].split("-")[1]);
    const url: string = `/api/${type === 'finemapping' ? 'finemapped_region' : 'conditional_region'}/${pheno}/lz-results/?` + new URLSearchParams({
        filter: `analysis in 3 and chromosome in '${chr}' and position ge ${start} and position le ${end}`, 
        add_anno: 'false'});
    return (url);
}


export const getFinemapCondData = ( 
    region: string,
    type: string,
    pheno: string,
    sink: (s: FinemapData.Data[]) => void,
    getURL = get) => { 
        getURL<any>(resolveURL(get_finemap_cond_region_url(region, type, pheno)), sink)
    };
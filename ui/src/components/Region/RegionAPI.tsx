import { Region, RegionParams } from "./RegionModel";
import { get, Handler } from "../../common/commonUtilities";
import { resolveURL } from "../Configuration/configurationModel";
import { Locus } from "../../common/commonModel";

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



export const finemap_url = (urlPartial : string, region: string) : string => {
    const chr = region.split(":")[0];
    const start = Number(region.split(":")[1].split("-")[0]);
    const end = Number(region.split(":")[1].split("-")[1])
    const url: string = `${urlPartial}results/?filter=analysis in 3 and chromosome in '${chr}' and position ge ${start} and position le ${end}&type=susie`;
    return (url)
}


export const getFinemapSusieData = ( 
    urlPartial: string, 
    region: string,
    sink: (s: any) => void,
    setError: (s: string | null) => void,
    getURL = get) => { 
        const handler : Handler = (url : string) => (e : Error) => setError(`finemap susie data ${e.message}`);
        getURL<any>(finemap_url(urlPartial, region),sink, handler)
    };
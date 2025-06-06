import { RegionParams, Summary} from "./regionModel";
import { get } from "../../common/commonUtilities";
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
                          sink: (s: Summary.Region) => void,
                          getURL = get) =>
    parameter &&  getURL<Summary.Region>(resolveURL(region_url(parameter)),sink)



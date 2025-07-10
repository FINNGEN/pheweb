import { RegionParams, Summary} from "./regionModel";
import { get, Handler } from '../../common/commonUtilities';
import { resolveURL } from "../Configuration/configurationModel";
import { Locus, locusToStr } from '../../common/commonModel';
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
 * @param handler
 */
export const getRegion = (parameter: RegionParams<Locus> | undefined,
                          sink: (s: Summary.Region) => void,
													setError: (s: string | null) => void,
                          getURL = get) => {
	const handler: Handler = (url: string) => (e: Error) => {
    setError(`for region ${parameter?.locus?locusToStr(parameter?.locus):'is missing'} and phenotype '${parameter?.phenotype}' error ${e.message} occurred at '${url}'`);
	}
	parameter && getURL<Summary.Region>(resolveURL(region_url(parameter)), sink, handler)
}


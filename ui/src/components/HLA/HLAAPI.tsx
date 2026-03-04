import { get, Handler } from "../../common/commonUtilities";
import { resolveURL } from "../Configuration/configurationModel";
import { HLAModel } from "./HLAModel";

export const getTopHLAResults = (
        sink: (s: HLAModel.Data) => void,
        getURL = get) : void => {
    getURL(resolveURL(`/api/v1/hla_summary/top`), sink)
}
import React from "react";
import RegionMessage from "./RegionMessage";
import RegionLocusZoom from "./RegionLocusZoom";
import RegionColocalization from "./RegionColocalization";
import RegionBanner from "./RegionBanner";
import RegionSummary from "./RegionSummary";
import RegionContextProvider from "./RegionContext";
import ColocalizationContextProvider from "./Colocalization/ColocalizationContext";
import RegionSelection from "./RegionSelection";
import { RouteComponentProps } from "react-router-dom";
import { RegionParams } from "./regionModel";
import {setPageTitle} from "../../common/commonUtilities";

type Props = RouteComponentProps<RegionParams>;

const Region = (props : Props) => {
    const {locus, phenotype} = props.match.params;
    const title : string = `region ${locus} ${phenotype}`;
    setPageTitle(title);

    return (
        <RegionContextProvider params={props.match.params}>
            <ColocalizationContextProvider params={props.match.params}>
                <div id="b85c6b35-146e-438d-a38a-2a80cd3b46f6" className="container-fluid"  style={{ width : "95%"}}>
                    <RegionBanner/>
                    <RegionSummary/>
                    <RegionSelection/>
                    <RegionMessage/>
                    <RegionLocusZoom/>
                    <RegionColocalization/>
                </div>
            </ColocalizationContextProvider>
          </RegionContextProvider>)
}

export default Region;

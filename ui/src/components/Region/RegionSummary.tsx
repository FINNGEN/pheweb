import React, { useContext } from "react";
import { RegionContext, RegionState } from "./RegionContext";
import RegionFinemapSummary from "./RegionFinemapSummary";

interface Props {}

const RegionSummary =  (props : Props) => {
    const { region } = useContext<Partial<RegionState>>(RegionContext);
    if(region) {
        const { phenotype } = region;
        return (<div className="row">
            <div id={"23813672-798b-46ec-a8ad-4eb2bf72b328"} className="pheno-info col-xs-12">
                <p><b>{phenotype.num_cases}</b> cases, <b>{phenotype.num_controls}</b> controls</p>
                <p>{phenotype.category}</p>
                { <RegionFinemapSummary/>}
            </div>
        </div>)
    } else {
        return (<div className="row"/>);
    }
}

export  default RegionSummary;

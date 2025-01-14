import React, { useContext } from "react";
import { RegionContext, RegionState } from "./RegionContext";
import RegionSelectFinemapping from "./LocusZoom/RegionSelectFinemapping";

interface Props {}

const RegionSummary =  (props : Props) => {
    const { region } = useContext<Partial<RegionState>>(RegionContext);
    if(region) {
        const { pheno } = region;
        return (<div className="row">
            <div className="pheno-info col-xs-12">
                <p><b>{pheno.num_cases}</b> cases, <b>{pheno.num_controls}</b> controls</p>
                <p>{pheno.category}</p>
                { <RegionSelectFinemapping/> }
            </div>
        </div>)
    } else {
        return (<div className="row"/>);
    }
}

export  default RegionSummary;

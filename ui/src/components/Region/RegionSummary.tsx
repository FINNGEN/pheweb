import React, { useContext } from "react";
import { RegionContext, RegionState } from "./RegionContext";
import RegionSelectFinemapping from "./LocusZoom/RegionSelectFinemapping";

interface Props {}

const RegionSummary =  (props : Props) => {
    const { region } = useContext<Partial<RegionState>>(RegionContext);
    if(region) {
        const { phenotype } = region;
        return (<div className="row">
            <div className="pheno-info col-xs-12">
                <p><b>{phenotype.num_cases}</b> cases, <b>{phenotype.num_controls}</b> controls</p>
                <p>{phenotype.category}</p>
                { <RegionSelectFinemapping/> }
            </div>
        </div>)
    } else {
        return (<div className="row"/>);
    }
}

export  default RegionSummary;

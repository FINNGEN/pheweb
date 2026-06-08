import React, { useContext } from "react";
import { RegionContext, RegionState } from "./RegionContext";
import RegionFinemapSummary from "./Finemapping/RegionFinemapSummary";

interface Props {}

const RegionSummary =  (props : Props) => {
    const { region } = useContext<Partial<RegionState>>(RegionContext);
    if(region) {
        const { phenotype } = region;
        return (<div className="pheno-info">
                <p><b>{phenotype.num_cases}</b> cases, <b>{phenotype.num_controls}</b> controls</p>
                <p>{phenotype.category}</p>
                { <RegionFinemapSummary/>}
            </div>)
    } else {
        return (<div/>);
    }
}

export  default RegionSummary;

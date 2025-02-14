import React, { useContext } from "react";
import { RegionContext, RegionState } from "./RegionContext";

interface Props {}

const RegionBanner =  (props : Props) => {
    const { region } = useContext<Partial<RegionState>>(RegionContext);
    if(region) {
        const phenotype = region.phenotype;

        return (<div className="row">
            <div className="col-xs-12">
            { /* RegionBanner */ }
                <h1>{phenotype && phenotype.phenostring} </h1>
                    <p>
                        <a href={`https://risteys.finregistry.fi/phenocode/${phenotype.phenocode}`}
                           rel="noopener noreferrer"
			   target="_blank">RISTEYS</a>
                    </p>
                </div>
            </div>);
    } else {
        return (<div className="col-xs-12"></div>);
    }

}

export default RegionBanner;
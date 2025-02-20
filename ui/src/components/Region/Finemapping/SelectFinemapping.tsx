import React from "react";
import {Summary} from "../regionModel";
import SelectFinemappingConditional from "./SelectFinemappingConditional";
import SelectFinemappingMethod from "./SelectFinemappingMethod";
import CredibleSetSummaryConditional = Summary.CredibleSetSummaryConditional;
import {regionSummaryTypes} from "../regionUtilities";

interface Props {
    show : boolean ,
    regionSummary : Summary.RegionSummary
}

const SelectFinemapping = ({ show , regionSummary }: Props) => {
    if(show) {
        const conditionalCredibleSet : CredibleSetSummaryConditional | undefined = regionSummary.credible_sets.find(x => x.type === 'conditional') as CredibleSetSummaryConditional | undefined;
        const conditionalComponent  = <SelectFinemappingConditional credibleSetSummaryConditional={conditionalCredibleSet}/>

        const types = new Set(regionSummaryTypes(regionSummary).filter(t => t === 'susie' || t === 'finemap'));
        const methods = Array.from(types);
        methods.sort().reverse();
        const finemappingMethod = <SelectFinemappingMethod methods={methods} locus={regionSummary.location} />
        return <>
            <div className="flex-row-container">
                {conditionalComponent}
            </div>
            <div className="flex-row-container">
                {finemappingMethod}
            </div>
        </>
    } else {
        return null;
    }
}

export default SelectFinemapping;
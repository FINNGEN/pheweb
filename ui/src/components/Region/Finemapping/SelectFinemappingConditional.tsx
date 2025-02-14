import React, {useContext} from "react";
import {range} from "../../../common/commonUtilities";
import CommonButtonSelector from "../../../common/CommonButtonSelector";
import conditionalSelectHook from "./conditionalSelectHook";
import {RegionContext, RegionState} from "../RegionContext";
import {Summary} from "../regionModel";
import CredibleSetSummaryConditional = Summary.CredibleSetSummaryConditional;

interface Props { credibleSetSummaryConditional: CredibleSetSummaryConditional | undefined }

const SelectFinemappingConditional = (props : Props) => {
    const credibleSetSummaryConditional : CredibleSetSummaryConditional | undefined =  props.credibleSetSummaryConditional;
    const {  locusZoomContext } = useContext<Partial<RegionState>>(RegionContext);
    const {setConditionalIndex } = conditionalSelectHook(locusZoomContext, credibleSetSummaryConditional)
    const n_signals : number | undefined = credibleSetSummaryConditional?.conditioned_on?.length;

    if(n_signals > 1){
        const signals : number[] = range(0, n_signals - 1);
        return <div className={"flex-row-container"}>
                Show conditioned on
                <span className={"region-spacer"}></span>
                <CommonButtonSelector options={signals} onSelect={setConditionalIndex}/>
                <span className={"region-spacer"}></span>
            </div>
    } else { return null; }

}



export default SelectFinemappingConditional;
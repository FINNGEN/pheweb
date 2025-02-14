import React, {useContext} from "react";
import {Summary} from "../regionModel";
import CommonButtonSelector from "../../../common/CommonButtonSelector";
import finemappingMethodHook from "./finemappingMethodHook";
import {RegionContext, RegionState} from "../RegionContext";
import {Locus} from "../../../common/commonModel";

interface Props {
    methods: Summary.RegionSummaryType[]
    locus : Locus
}

const SelectFinemappingMethod =     ( props : Props) => {
    const methods: Summary.RegionSummaryType[] = props.methods;
    const locus : Locus = props.locus;
    const { locusZoomContext } = useContext<Partial<RegionState>>(RegionContext);
    const { setRegionSummaryType } = finemappingMethodHook(locusZoomContext, locus);
    let view = <></>;
    if (methods.length > 1) {
        view = <>
            Select Finemap From
            <span className={"region-spacer"}></span>
            <CommonButtonSelector options={methods} onSelect={setRegionSummaryType}/>
            <span className={"region-spacer"}></span>
        </>
    }
    return view;

}

export default  SelectFinemappingMethod;
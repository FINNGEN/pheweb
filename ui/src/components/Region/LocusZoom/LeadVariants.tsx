import React, { Fragment, useEffect, useState, useContext } from "react";
import '../Region.css'
import './leadVariants.css'
import {
    FinemappingRegion,
    RegionSummary,
} from "../RegionModel";
import {RegionContext, RegionState} from "../RegionContext";

const region_url = (phenotype : string, chromosome : number, position : number) => `/region/${phenotype}/${chromosome}:${Math.max(position - 200 * 1000, 0)}-${position + 200 * 1000}`

const LeadVariants = (props: { regionSummary: RegionSummary, show: boolean, index : number} ) => {
    const { region } = useContext<Partial<RegionState>>(RegionContext);
    const phenocode: string = region.phenotype.phenocode;
    const regionSummary: RegionSummary = props.regionSummary;
    const lead_variants : FinemappingRegion[] = regionSummary.lead_variants;
    const render = (i : number, j : number, fmr : FinemappingRegion,phenotype : string)=> {
        const key = `${i}-${j}-div`;
        return (<div style={{marginLeft: "7px"}} key={key}>
            <a href={region_url(phenotype,fmr.chr,fmr.position)} key={key}>
                {fmr.chr}:{fmr.position}:{fmr.ref}:{fmr.alt}
            </a>
        </div>
    )
    }
    return (
        <Fragment>
            {
                lead_variants && props.show ?
                    <Fragment>
                        <div className="flex-row-container"> Lead variants:
                            Lead Variants: { lead_variants.map((x,j) =>render(props.index,j,x,phenocode)) }
                        </div>
                      </Fragment>
                : null
            }
        </Fragment>
    )
}


export default LeadVariants;

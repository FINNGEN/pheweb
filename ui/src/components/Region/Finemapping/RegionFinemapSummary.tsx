import React, {Fragment, useContext, useState} from "react";
import {RegionContext, RegionState} from "../RegionContext";
import {Summary} from "../regionModel";
import CredibleSetSummary = Summary.CredibleSetSummary;
import {capitalizeFirstLetter, partition, range, toSorted} from "../../../common/commonUtilities";
import SelectFinemapping from "./SelectFinemapping";
import CredibleSetVariant from "./CredibleSetVariant";
import {regionLabel, regionSummaryTypes, regionURL} from "../regionUtilities";
import SusieLeadVariants from "./SusieLeadVariants";


const credibleSetComponent = (phenotype: string, cs: CredibleSetSummary<Summary.RegionSummaryType>, csId: number , regionId : number) => {
    const key = `credible-set-region-${regionId}-${csId}-${cs.type}`
    return [ <div key={`header-region-counts-${key}`} className={"flex-row-container"}>
                {cs.n_signals} {cs.type} signals {cs.type === 'finemap' ? `( prob. ${cs.n_signals_prob.toFixed(3)} )` : ''}
            </div>,
            <div key={`header-region-detail-${key}`} className={"flex-row-container"}>
                {Summary.isCredibleSetSummarySusie(cs) ?
                    <SusieLeadVariants  cs={cs} phenotype={phenotype} regionId={regionId} /> :
                    <>Lead Variant : {
                        cs.lead_variants.map(
                            (variant, i) =>
                                <Fragment key={i}>
                                    <CredibleSetVariant phenotype={phenotype} cs={cs} variant={variant} />
                                </Fragment>
                        )}</>
                }
            </div>]
}

const RegionFinemapSummary = (props: any) => {

    const { region } = useContext<Partial<RegionState>>(RegionContext);
    const [showRegion, setShowRegion] = useState<number | null>(region?.region_summary?.length > 0 ? 0 : null);

    const handleAddNumber = (i: number) => {
        setShowRegion(i);
    };
    const hasRegions = region?.region_summary?.length > 0
    const hasOverlappingRegions = region?.region_summary?.length > 1;
    const phenocode = region.phenotype.phenocode;
    return <>
       {hasRegions &&
        <div className={"flex-row-container"}>
            {region?.region_summary && hasOverlappingRegions ? `${region?.region_summary?.length} Overlapping` : ""} Finemapping/conditional
            regions
        </div>}
        {region.region_summary.map((regionSummary, i) => <div key={`summary-${i}`}>
            <div className={"flex-row-container"} onClick={() => handleAddNumber(i)}>
                <div className="arrow-container">
                    <div className={`arrow ${i == showRegion ? 'down' : 'up'}`}></div>
                </div>

                <span className={'region-range'}>
                    {hasOverlappingRegions ?
                        <a href={regionURL(phenocode, regionSummary.location)}>
                            {regionLabel(regionSummary.location)}
                        </a>
                        : regionLabel(regionSummary.location)
                    }

                </span>
                <span
                    className={'region-count'}>{toSorted(regionSummaryTypes(regionSummary)).map(capitalizeFirstLetter).join(', ')}</span>
            </div>

            {(i == showRegion) && regionSummary.credible_sets.flatMap((cs, csId) => credibleSetComponent(phenocode, cs, csId, i)) }

            <SelectFinemapping regionSummary={regionSummary} show={i === showRegion}/>
        </div>)
        }
        <div className={"flex-row-container"}>
            Conditional analysis results are approximations from summary stats. Conditioning is repeated until no signal
            p &lt; 1e-6 is left.
        </div>

    </>;
}

export default RegionFinemapSummary;
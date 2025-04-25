import {Summary} from "../regionModel";
import {partition} from "../../../common/commonUtilities";
import React, {Fragment} from "react";
import CredibleSetVariant from "./CredibleSetVariant";

const SusieLeadVariants = ({ phenotype , cs , regionId } : { phenotype: string, cs: Summary.CredibleSetSummarySusie , regionId : number  }) => {
    const [low_purity, high_purity] = partition<Summary.SusieCredibleSet>(cs.lead_variants, c => c.low_purity == 1)
    const low_purity_render = low_purity && low_purity.length > 0 ? <>Low
        purity {low_purity.map((variant, i) =>
            <Fragment key={`region-${regionId}-low-${i}`}>
                <CredibleSetVariant phenotype={phenotype} cs={cs} variant={variant}  />
            </Fragment>
        )}</> : null;
    const high_purity_render = high_purity && high_purity.length > 0 ? <>High
        purity {high_purity.map((variant, i) =>
            <Fragment key={`highregion-${regionId}-${i}`}>
                <CredibleSetVariant phenotype={phenotype} cs={cs} variant={variant} />
            </Fragment>
        )}</> : null;
    return <>{low_purity_render} {high_purity_render}</>;
}

export default SusieLeadVariants;
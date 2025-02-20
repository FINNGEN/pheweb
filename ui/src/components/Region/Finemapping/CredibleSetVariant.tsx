import React from "react";
import {Summary} from "../regionModel";
import VariantLink from "./VariantLink";
import {variantTooltip} from "./variantTooltip";
import CredibleSetSummary = Summary.CredibleSetSummary;


interface Props {
    phenotype: string,
    cs: CredibleSetSummary<Summary.RegionSummaryType>
    variant: Summary.FinemappingCS
}

const CredibleSetVariant = ({ phenotype , cs , variant } : Props) => {
    const type = cs.type;
    const key = `${type}-${variant.position}:${variant.alt}:${variant.ref}`;
    const url = `/region/${phenotype}/${variant.chr}:${Math.max(variant.position - 200 * 1000, 0)}-${variant.position + 200 * 1000}`
    const data_tip: string = variantTooltip(cs, variant);
    const label = `${variant.chr}:${variant.position}:${variant.alt}:${variant.ref}`;
    return <VariantLink  key={key} url={url} data_tip={data_tip} label={label}/>;
}

export default CredibleSetVariant;
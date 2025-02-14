import React from "react";
import {Summary} from "../regionModel";
import ReactDOMServer from "react-dom/server";
import VariantLink from "./VariantLink";

interface Props {
    phenotype: string,
    type: Summary.RegionSummaryType
    variant: Summary.FinemappingCS
}

const dataTip = (type: Summary.RegionSummaryType, variant: Summary.FinemappingCS) => {
    if (type === 'finemap') {
        const v = variant as Summary.FinemapCredibleSet;
        return <>
            cs : {v.cs}<br/>
            prob : {v.prob}<br/>
        </>
    }
    if (type === 'susie') {
        const v = variant as Summary.SusieCredibleSet;
        return <>
            cs : {v.cs}<br/>
            low purity : {v.low_purity == 1 ? 'true' : 'false'}<br/>
            id : {v.id}<br/>
            prob : {v.prob}<br/>
            rsid : {v.rsid}<br/>
        </>
    }
    if (type === 'conditional') {
        const v = variant as Summary.ConditionedCredibleSet;
        return <>
            varid : {v.varid}<br/>
            pvalue : {v.pvalue}<br/>
            beta : {v.beta}<br/>
            pvalue : {v.pvalue}<br/>
            maf : {v.maf}<br/>
            id : {v.id}<br/>
        </>
    }
}

const CredibleSetVariant = ({ phenotype , type , variant } : Props) => {
    const key = `${type}-${variant.position}:${variant.alt}:${variant.ref}`;
    const url = `/region/${phenotype}/${variant.chr}:${Math.max(variant.position - 200 * 1000, 0)}-${variant.position + 200 * 1000}`
    const data_tip: string = ReactDOMServer.renderToStaticMarkup(dataTip(type, variant));
    const label = `${variant.chr}:${variant.position}:${variant.alt}:${variant.ref}`;
    return <VariantLink  key={key} url={url} data_tip={data_tip} label={label}/>;
}

export default CredibleSetVariant;
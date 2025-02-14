import React from "react";
import ReactTooltip from "react-tooltip";

interface VariantLinkProps {
    url: string,
    data_tip: string,
    label: string
}

const VariantLink = ({ url , data_tip , label }: VariantLinkProps) => <div style={{marginLeft: "7px"}}>
    <ReactTooltip
        className="tooltip-lead-vars"
        id='tooltip-lead-vars'
        html={true}
        arrowColor="#F4F4F4"
        effect='solid'
    />
    <a href={url} className={"region-variant"}>
                    <span data-tip={data_tip}
                          data-for="tooltip-lead-vars">{label}
                    </span>
    </a>
</div>

export default  VariantLink;
import {Summary} from "../regionModel";
import {mustacheDiv} from "../../../common/commonUtilities";
import {ConfigurationWindow} from "../../Configuration/configurationModel";
import * as Handlebars from "handlebars/dist/cjs/handlebars";
import CredibleSetSummary = Summary.CredibleSetSummary;

declare let window: ConfigurationWindow;
const { config } = window;
const variant_popup = config?.userInterface?.region?.variant_popup;

const default_finemap_popup = `
            cs : {{cs}}<br/>
            pip : {{#prob}}{{decimalFormatter .}}{{/prob}}<br/>`
const finemap_popup = variant_popup?.finemap_popup || default_finemap_popup;

const default_susie_popup = `
            cs : {{cs}}<br/>
            low purity : {{is_low_purity}}<br/>
            {{#maf}}maf : {{decimalFormatter .}}<br/>{{/maf}}
            pip : {{prob}}<br/>
        `
const susie_popup = variant_popup?.susie_popup || default_susie_popup;

const default_conditional_popup = `
            beta : {{#beta}}{{decimalFormatter .}}{{/beta}}<br/>
            sebeta: {{#sebeta}}{{decimalFormatter .}}{{/sebeta}}<br/>
            pvalue : {{#pvalue}}{{scientificFormatter .}}{{/pvalue}}<br/>
            maf : {{#maf}}{{decimalFormatter .}}{{/maf}}<br/>
        `
const conditional_popup = variant_popup?.conditional_popup || default_conditional_popup;

export const variantTooltip = (cs: CredibleSetSummary<Summary.RegionSummaryType>, variant: Summary.FinemappingCS) : string => {
    const type = cs.type;
    if (type === 'finemap') {
        const v = variant as Summary.FinemapCredibleSet;
        return Handlebars.compile(finemap_popup)(v);
    }
    if (type === 'susie') {
        const v = variant as Summary.SusieCredibleSet;
        return Handlebars.compile(susie_popup)({ ... v, is_low_purity:v.low_purity == 1 });
    }
    if (type === 'conditional') {
        const v = variant as Summary.ConditionedCredibleSet;
        const c : Summary.CredibleSetSummaryConditional = cs as Summary.CredibleSetSummaryConditional
        return Handlebars.compile(conditional_popup)({... v , conditioned_on : c.conditioned_on });
    }
}

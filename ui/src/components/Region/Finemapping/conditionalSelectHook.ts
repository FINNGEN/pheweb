import { useState, useEffect } from "react";
import {DataSources, Plot} from "locuszoom";
import {Summary , Locuszoom } from "../regionModel";
import Params = Locuszoom.Params;
import {LocusZoomContext} from "../LocusZoom/regionLocusZoomHook";
import CredibleSetSummaryConditional = Summary.CredibleSetSummaryConditional;

const conditionalSelectHook = (locusZoomContext : LocusZoomContext | undefined,
                               credibleSetSummaryConditional : CredibleSetSummaryConditional | undefined) => {
    const n_signals : number | undefined = credibleSetSummaryConditional?.conditioned_on?.length;
    const plot: Plot | undefined = locusZoomContext?.plot;
    const dataSources: DataSources | undefined = locusZoomContext?.dataSources;
    const conditionedOn : string[] | undefined = credibleSetSummaryConditional?.conditioned_on
    const [conditionalIndex, setConditionalIndex] = useState<number | null>(n_signals > 0?0:null);

    useEffect(() => {
        const params = dataSources?.sources?.conditional?.params as Params;
        if(plot?.panels && conditionalIndex !== undefined && conditionalIndex !== null){
            const conditionalOnVariants = conditionedOn[conditionalIndex];
            const panel = plot.panels.conditional;
            panel.setTitle(`conditioned on ${conditionalOnVariants}`);
        }

        if (dataSources && params?.allData && plot?.panels && conditionalIndex !== undefined && conditionalIndex !== null) {
            const conditionalOnVariants = conditionedOn[conditionalIndex];
            const panel = plot.panels.conditional;

            const data = params.allData?.find(x => x.conditioned_on === conditionalOnVariants)
            if(data){
                panel.data_layers['associationpvalues'].data = dataSources.sources.conditional.parseArraysToObjects(data.data, params.fields, params.outnames, params.trans);
                panel.data_layers['associationpvalues'].render();
            }
        } else if(dataSources && params?.allData && plot?.panels && conditionalIndex === null){
            const panel = plot.panels.conditional;
            panel.data_layers['associationpvalues'].data = [];
            panel.data_layers['associationpvalues'].render();
        }
    },[conditionalIndex]);

    return {setConditionalIndex };
}

export default conditionalSelectHook;
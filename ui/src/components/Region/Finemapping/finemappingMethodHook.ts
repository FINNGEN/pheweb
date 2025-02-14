import {LocusZoomContext} from "../LocusZoom/regionLocusZoomHook";
import {useEffect, useState} from "react";
import {Locuszoom, Summary} from "../regionModel";
import {DataSources, Plot} from "locuszoom";
import Params = Locuszoom.Params;
import {Locus, locusToStr} from "../../../common/commonModel";

const finemappingMethodHook = (locusZoomContext : LocusZoomContext, locus : Locus) => {
    const [regionSummaryType, setRegionSummaryType] = useState<Summary.RegionSummaryType | null>(null);
    const plot: Plot | undefined = locusZoomContext?.plot;
    const dataSources: DataSources | undefined = locusZoomContext?.dataSources;


    useEffect(() => {
        const params = dataSources?.sources?.finemapping?.params as Params;
            if (plot?.panels && plot?.panels?.finemapping && regionSummaryType !== null) {
                const panel = plot.panels.finemapping;
                panel.setTitle(`${regionSummaryType} credible sets`);
            }

            if(dataSources && params?.allData && plot?.panels){
                const index : number = params.allData.findIndex((cur) => cur.type === regionSummaryType && cur.region == locusToStr(locus));
                if(index > -1){
                    params.dataIndex = index;
                    const panel = plot.panels.finemapping;
                    panel.data_layers["associationpvalues"].data = dataSources.sources.finemapping.parseArraysToObjects(params.allData[index].data, params.fields, params.outnames, params.trans)
                    panel.data_layers["associationpvalues"].render();
                }
            }
        },[regionSummaryType]);

    return {setRegionSummaryType}
}

export default finemappingMethodHook;

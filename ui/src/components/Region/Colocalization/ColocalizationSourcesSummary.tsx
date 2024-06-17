
import React, { useState, useEffect } from "react";
import { ColocalizationSourceType } from "./ColocalizationModel";
import { ConfigurationWindow } from "../../Configuration/configurationModel";
import {colocTypesSummaryData as Data} from '../../../common/commonModel'

import './Colocalization.css'


declare let window: ConfigurationWindow;
const { config } = window;
const colocalizationSourceTypes : ColocalizationSourceType[]|null = config?.userInterface?.region?.colocalization?.colocalizationSourceTypes || null;


const ColocalizationSourcesSummary = ( props: {data: Data[], showSourceTypes: boolean}) => {

    const [sourceSummaryData, setSourceSummaryData] = useState<Data[] | null>(null);
    const [displaynameSources, setDisplaynameSources]  = useState<String[] | null>(null);
    const [sources, setSources]  = useState<String[] | null>(null);

    const filterSource = (data, attribute) => {
        var arr = data?.map(element => {return element[attribute]});
        var src = arr?.filter((item,index) => arr?.indexOf(item) === index);
        return(src)
    }

    useEffect(() => {
        setSourceSummaryData(props.data);
    }, [props]);

    useEffect(() => {
        sourceSummaryData && setDisplaynameSources(filterSource([...sourceSummaryData], 'source'));
        sourceSummaryData && setSources(filterSource([...sourceSummaryData], 'sourceKey'));   
    }, [sourceSummaryData]);

    const renderContent = (src, data) => (
        src?.map((key, i) => 
        <div className="colocs-summary-text" key={i}>{key}: 
            <span className="colocs-summary-pos"> <b>↑</b>
                {data?.filter(element => element.beta > 0 && element.source == key).length}
            </span>
            <span className="colocs-summary-neg"> <b>↓</b>
                {data?.filter(element => element.beta <= 0 && element.source == key).length}
            </span>
        </div>)
    )

    return (
        <div className="colocs-summary">
        {
            colocalizationSourceTypes!==null && props.showSourceTypes ? 
            <div className="colocs-summary-row" > 
            {
                sourceSummaryData && colocalizationSourceTypes.map((item, i) => {
                    
                    var sourcesFilt = [...item['sources']].filter((element, index) => sources?.indexOf(element) >= 0);
                    var sourceSummaryDataFilt = [...sourceSummaryData].filter((element, index) => sourcesFilt.indexOf(element.sourceKey) >= 0);
                    var displaySourcesType = [...new Set(sourceSummaryDataFilt.map(element => element.source))];
    
                    if (sourceSummaryDataFilt.length > 0) {
                        return ( 
                        <div className="colocs-summary-type">
                            <b>{item['type']}:</b><div className="colocs-summary-row">{renderContent(displaySourcesType, sourceSummaryDataFilt)}</div>
                        </div>)
                    }
                }) 
            }
            </div> : <div className="colocs-summary-row" >{ renderContent(displaynameSources, sourceSummaryData)}</div> 
        }
        </div>       
    )
};

export default ColocalizationSourcesSummary;


import React, { Fragment, useContext, useEffect, useState } from "react";
import {CondFMRegions, layout_types, Params, RegionSummary, RegionSummaryType} from "../RegionModel";
import { RegionContext, RegionState } from "../RegionContext";
import LeadVariants from './LeadVariants'
import region from "../Region";


const Component = (region_summary : RegionSummary[], dataSources , plot) => {
    const finemapping_methods : layout_types[] =
      Array.from( (region_summary || [])
        .filter(r => r.type === 'susie' || r.type === 'finemap')
        .reduce((acc,value) => {acc.add(value.type); return acc; } ,
          new Set<layout_types>()))

    const [selectedMethod, setSelectedMethod] = useState<layout_types | undefined>(finemapping_methods.length > 0?finemapping_methods[0]:undefined);
    const cond_signals : RegionSummary | undefined = (region_summary || []).find(region => region.type === 'conditional')
    const n_cond_signals = cond_signals?.n_signals || 0
    const [conditionalIndex, setConditionalIndex] = useState<number | undefined>(n_cond_signals > 0?0:undefined);
    const finemap : RegionSummary | undefined = (region_summary || []).find(region => region.type === 'finemap' || region.type === 'susie');
    const finemappedCondRegion: string = `${finemap.chr}:${finemap.start}-${finemap.end}` || null;

    const [showLeadvars, setShowLeadvars] = useState< {
        susie: boolean;
        finemap: boolean;
        conditional: boolean;
    }>({susie: false, finemap: false, conditional: false});

    useEffect(() => {
        const params = dataSources?.sources?.finemapping?.params as Params ;

        if(plot?.panels && selectedMethod){
            const panel = plot.panels.finemapping
            panel.setTitle(`${selectedMethod} credible sets`)
        }

        if(dataSources && params?.allData && plot?.panels){
            const index : number = params.allData.findIndex((cur) => cur.type === selectedMethod);
            params.dataIndex = index;
            const panel = plot.panels.finemapping;
	    panel.data_layers.associationpvalues.data = dataSources.sources.finemapping.parseArraysToObjects(params.allData[index].data, params.fields, params.outnames, params.trans)
            panel.data_layers.associationpvalues.render();
       }

    },[setSelectedMethod, selectedMethod, dataSources, plot]);

    useEffect(() => {
        const params = dataSources?.sources?.conditional?.params as Params;

        if(dataSources && params?.allData && plot?.panels && conditionalIndex!==undefined) {
            params.dataIndex = conditionalIndex;
            const panel = plot.panels.conditional;
            panel.setTitle('conditioned on ' + params.allData[conditionalIndex].conditioned_on);
            panel.data_layers.associationpvalues.data = dataSources.sources.conditional.parseArraysToObjects(params.allData[conditionalIndex].data, params.fields, params.outnames, params.trans);
            panel.data_layers.associationpvalues.render();
        }
        
    },[setConditionalIndex, conditionalIndex, dataSources, plot]);

    const showConditional = (i : number) => () => dataSources && plot && setConditionalIndex(i) ;

    const showFinemapping = (s : layout_types) => () => { 
        dataSources && plot &&  setSelectedMethod(s); 
    }
          
    const signalLabel = (regionSummary : RegionSummary, i : number) => {
        return (
            <Fragment>
            <div className="flex-row-container">
            <div className="arrow-container">
                <div className={`arrow ${showLeadvars[regionSummary.type] ? "up" : "down"}`} onClick={() => setShowLeadvars(prev => ({...prev, [regionSummary.type]: !showLeadvars[regionSummary.type]})) }></div>
            </div>
            {
                regionSummary.type !== 'finemap' ?
                <Fragment>
                    <span>{regionSummary.n_signals} {regionSummary.type} signals </span><br/>
                </Fragment> 
                : <Fragment>
                    <span>{regionSummary.n_signals} {regionSummary.type} signals (prob. {regionSummary.n_signals_prob.toFixed(3)})</span>
                </Fragment>
            }
            </div> 
            <LeadVariants regionSummary={regionSummary} show={showLeadvars[regionSummary.type]} index={i}/>
            </Fragment>
            )
        }
          
    const conditionalLabel = (i : number) => <button onClick={showConditional(i)}
                                                     key={i}
                                                     data-cond-i={i}
                                                     disabled={ i === conditionalIndex }
                                                     className={"btn " + (i === conditionalIndex ? 'btn-default' : 'btn-primary' )}>
        <span>{i + 1}</span>
    </button>

    let summaryHTML =

    <Fragment>
          
          <span>Finemapping/conditional region: <b>{finemappedCondRegion}</b></span>
          { region_summary.map((region,i) => <div key={i}>{  signalLabel(region, i) }</div>)}

          {n_cond_signals > 0 ?
            <Fragment>
                <div className="row">
                    <div className="col-xs-12">
                        <p>
                            <span>Conditional analysis results are approximations from summary stats. Conditioning is repeated until no signal p &lt; 1e-6 is left.</span>
                        </p>
                    </div>
                </div>
                <div className="row">
                    <div className="col-xs-12">
                        <p>
                            <span>Show conditioned on { Array.from(Array(n_cond_signals).keys()).map(i => conditionalLabel(i)) } variants<br/></span>
                        </p>
                    </div>
                </div>
            </Fragment> :
            <Fragment/>
          }

          { (finemapping_methods.length > 0) ?
            <Fragment>Show fine-mapping from </Fragment> : <Fragment/> }

          { finemapping_methods.map((r,i) =>
            <button type="button" key={i} onClick={showFinemapping( r )}
            className={"btn " + (r === selectedMethod ? 'btn-default' : 'btn-primary' )}
            disabled={ r === selectedMethod }>
        <span>{ r }</span>
    </button>
            )
          }

      </Fragment>
    return summaryHTML
}

export const RegionSelectFinemapping = () => {

    const { region : {region_summary} = {} ,
            locusZoomContext : { dataSources , plot } = {} } = useContext<Partial<RegionState>>(RegionContext);

    let summaryHTML;
    if (region_summary && region_summary.length > 0)
    { summaryHTML = Component(region_summary, dataSources , plot) }
    else
    { summaryHTML = <Fragment/> }

    return summaryHTML;
}

export default RegionSelectFinemapping;

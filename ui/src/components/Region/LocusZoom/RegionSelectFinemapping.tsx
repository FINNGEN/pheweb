import React, { Fragment, useContext, useEffect, useState } from "react";
import { cond_fm_regions_types, CondFMRegions, layout_types, Params, LeadVariant } from "../RegionModel";
import { RegionContext, RegionState } from "../RegionContext";
import { async } from "q";
import { setData } from "../../Chip/features/chipTableSlice";
import { getFinemapSusieData } from '../RegionAPI';
import ReactTooltip from "react-tooltip";

import "../Region.css"

const getMaxIndex = (x: Array<number> ) : number => x.indexOf(Math.max(...x));
const indexOfAll = (arr, val) => arr.reduce((acc, el, i) => (el === val ? [...acc, i] : acc), []);

const Component = (cond_fm_regions : cond_fm_regions_types, dataSources , plot) => {
    const finemapping_methods : layout_types[] =
      Array.from( (cond_fm_regions || [])
        .filter(r => r.type === 'susie' || r.type === 'finemap')
        .reduce((acc,value) => {acc.add(value.type); return acc; } ,
          new Set<layout_types>()))

    const [selectedMethod, setSelectedMethod] = useState<layout_types | undefined>(finemapping_methods.length > 0?finemapping_methods[0]:undefined);
    const cond_signals : CondFMRegions | undefined = (cond_fm_regions || []).find(region => region.type === 'conditional')
    const n_cond_signals = cond_signals?.n_signals || 0
    const [conditionalIndex, setConditionalIndex] = useState<number | undefined>(n_cond_signals > 0?0:undefined);
    
    const { region } = useContext<Partial<RegionState>>(RegionContext);
    const finemap : CondFMRegions | undefined = (cond_fm_regions || []).find(region => region.type === 'finemap');
    const finemappedRegion: string = `${finemap.chr}:${finemap.start}-${finemap.end}` || null;
    const [finemapSusieData, setFinemapSusieData] = useState<any>(null);
    const [leadVariants, setLeadVariants] = useState<LeadVariant[]|[]>([]);
    const pheno = region.pheno.phenocode;
    const [errorFinemapSusie, setErrorFinemapSusie] = useState<string|null>(null);
    
    useEffect(() => { 
        const urlPartial: string = dataSources?.sources?.finemapping?.url;
        if (urlPartial){
            getFinemapSusieData(urlPartial, region.region, setFinemapSusieData, setErrorFinemapSusie);
        }
    },[dataSources]);

    useEffect(() => {
        errorFinemapSusie && console.error(errorFinemapSusie)
    }, [errorFinemapSusie])

    useEffect(() => {
        if (finemapSusieData) {
            const data = finemapSusieData[0].data;
            const cs = data.cs.filter((val, ind, arr) => arr.indexOf(val) == ind);
            
            cs.map(e => {
                const indices = indexOfAll([...data.cs], e);
                const probs = indices.map(i => [...data.prob][i]);
                setLeadVariants(arr => [...arr, {
                    cs: e,
                    csSize: indices.length, 
                    prob: probs[getMaxIndex(probs)], 
                    varid: indices.map(i => [...data.rsid][i])[getMaxIndex(probs)],
                    chr: indices.map(i => [...data.chr][i])[getMaxIndex(probs)],
                    pos: indices.map(i => [...data.position][i])[getMaxIndex(probs)],
                    pheno: pheno
                }]);
            });
        }
    }, [finemapSusieData]);

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

    const leadVarsContent = leadVariants.map((key, i) => { 

        const url: string = `/region/${key.pheno}/${key.chr}:${Math.max(key.pos - 200 * 1000, 0)}-${key.pos + 200 * 1000}`;

        return (
            <div style={{ marginLeft: "7px"}}>
                <ReactTooltip 
                className="tooltip-lead-vars"
                id='tooltip-lead-vars' 
                html={true}
                arrowColor="#F4F4F4"
                effect='solid'/>
                <a href={url}><span data-tip={
                    `<div style={{display: "flex", flexDirection: "column"}}>
                        <span>
                        <b>CS:</b> ${key.cs}<br>
                        <b>CS specific prob:</b> ${key.prob}<br>
                        <b>CS size:</b> ${key.csSize}</span>
                    </div>`
                } data-for="tooltip-lead-vars">{key.varid}</span></a>
            </div>
        )
        }
    )

    const signalLabel = (region : CondFMRegions) => region.type !== 'finemap' ?
        <Fragment>
            <span>{region.n_signals} {region.type} signals </span><br/>
            { leadVariants.length > 0 && region.type !== 'conditional' ? 
                <span style={{display: "flex", flexDirection: "row"}}>Lead variants: { 
                    leadVarsContent.slice(1).reduce(function(xs, x, i) {
                        return (xs.concat([(<span>,</span>), x]));
                    }, [leadVarsContent[0]])
                    }</span> 
                : null 
            } </Fragment> 
        : <Fragment>
            <span>{region.n_signals} {region.type} signals in finemapping region <b>{finemappedRegion}</b> (prob. {region.n_signals_prob.toFixed(3)})</span>
        </Fragment>
          
    const conditionalLabel = (i : number) => <button onClick={showConditional(i)}
                                                     key={i}
                                                     data-cond-i={i}
                                                     disabled={ i === conditionalIndex }
                                                     className={"btn " + (i === conditionalIndex ? 'btn-default' : 'btn-primary' )}>
        <span>{i + 1}</span>
    </button>

    let summaryHTML =

    <Fragment>
            
          { cond_fm_regions.map((region,i) => <div key={i}>{  signalLabel(region) }</div>)}

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

    const { region : {cond_fm_regions} = {} ,
            locusZoomContext : { dataSources , plot } = {} } = useContext<Partial<RegionState>>(RegionContext);

    let summaryHTML;
    if (cond_fm_regions && cond_fm_regions.length > 0)
    { summaryHTML = Component(cond_fm_regions, dataSources , plot) }
    else
    { summaryHTML = <Fragment/> }

    return summaryHTML;
}

export default RegionSelectFinemapping;

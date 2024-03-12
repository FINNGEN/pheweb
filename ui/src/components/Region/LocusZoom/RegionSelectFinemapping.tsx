import React, { Fragment, useContext, useEffect, useState } from "react";
import { cond_fm_regions_types, CondFMRegions, layout_types, Params } from "../RegionModel";
import { RegionContext, RegionState } from "../RegionContext";

export interface LeadCSVariants {
    variant: string;
	url: string;
}

function intersperse(arr, sep) {
    if (arr.length === 0) {
        return [];
    }

    return arr.slice(1).reduce(function(xs, x, i) {
        return xs.concat([sep, x]);
    }, [arr[0]]);
}

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
    const pheno = region?.pheno.phenocode;
    const finemap : CondFMRegions | undefined = (cond_fm_regions || []).find(region => region.type === 'finemap');
    const finemappedRegion: string = `${finemap.chr}:${finemap.start}-${finemap.end}` || null

    const leadVariantsCS = finemap?.lead_causal_vars.map(element => {
            let pos = Number(element.split('_')[1]);
            let chrom = Number(element.split('_')[0].replace('chr', ''));
            let result = {
                'variant': element.replaceAll('_', ':').replace('chr', ''), 
                'url': `/region/${pheno}/${chrom}:${Math.max(pos - 200 * 1000, 0)}-${pos + 200 * 1000}`
            };
            return result;
    });

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

    const showFinemapping = (s : layout_types) => () => { dataSources && plot &&  setSelectedMethod(s); }

    var leadVariantsCSjsx = leadVariantsCS.map((element, i) => {
        const split = element['url'].split('/');
        const tooltip = `Link to the region centered around the variant: ${split[split.length-1]}`;
        return <span><a title={tooltip} href={element['url']}>{element['variant']}</a></span>
    });
    leadVariantsCSjsx = intersperse(leadVariantsCSjsx, ', ');

    const signalLabel = (region : CondFMRegions) => region.type === 'finemap' ?
      <Fragment>
        <div>{region.n_signals} {region.type} signals (prob. {region.n_signals_prob.toFixed(3)})</div>
        <div>Lead variants: {leadVariantsCSjsx}</div>
        <div>Finemap region: {finemappedRegion} </div>
      </Fragment> :
      <Fragment><span>{region.n_signals} {region.type} signals </span><br/></Fragment>

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
            </button>)
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

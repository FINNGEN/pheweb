import React, { Fragment, useEffect, useState, useContext } from "react";
import ReactTooltip from "react-tooltip";
import { numberFormatter, scientificFormatter } from '../../../common/commonFormatter'
import { FinemapData } from "./RegionModel";
import { RegionContext, RegionState } from "../RegionContext";
import { getFinemapCondData } from '../RegionAPI';
import '../Region.css'


const getMaxIndex = (x: Array<number> ) : number => x.indexOf(Math.max(...x));
const indexAll = (arr, val) => arr.reduce((acc, el, i) => (el === val ? [...acc, i] : acc), []);



const LeadVariants = (props: { type: string, show: boolean} ) => {

    const { region } = useContext<Partial<RegionState>>(RegionContext);
    const pheno: string = region.pheno.phenocode;
    const [data, setData] = useState<FinemapData.Data[]|undefined>(undefined);
    const [leadVariants, setLeadVariants] = useState<FinemapData.LeadVariant[]|[]>([]);

    useEffect(() => { 
        getFinemapCondData(region.region,  props.type !== 'conditional' ? 'finemapping' : 'conditional', pheno, setData);
    }, []);

    useEffect(() => {

        var result: FinemapData.LeadVariant[] = [];
        const dataSelectedType: FinemapData.Data[] = props.type !== 'conditional' && data ? [data.find(element => element.type == props.type)] : data;

        dataSelectedType && dataSelectedType.map((element, i) => {
            if (element.type === 'conditional') {

                const ind: number = getMaxIndex(element.data.pvalue.map(x => -1*Math.log(x)));
                const pos: number = element.data.position[ind];
                const chr: string = element.data.chr[ind];
                                
                result.push({
                    pvalue: scientificFormatter(element.data.pvalue[ind]),
                    varid: element.data.id[ind].replaceAll('/', ':').replaceAll('_', ':'),
                    region_url:`/region/${pheno}/${chr}:${Math.max(pos - 200 * 1000, 0)}-${pos + 200 * 1000}`,
                    conditioned_on: element.conditioned_on.replaceAll('/', ':').replaceAll('_', ':')
                });
                
            } else {
                const groups: Array<string|number> = element.data.cs.filter((val, ind, arr) => arr.indexOf(val) == ind);
                groups.forEach(g => {

                    const csIndices: Array<number> = indexAll(element.data.cs, g);
                    const probs: Array<number> = csIndices.map(i => element.data.prob[i]);
                    const ind: number = getMaxIndex(probs); 
                    const chr: string = csIndices.map(i => element.data.chr[i])[ind];
                    const pos: number = Number(csIndices.map(i => element.data.position[i])[ind]);
                    result.push({
                        cs_specific_prob: numberFormatter(probs[ind]),
                        cs: g, 
                        cs_size: csIndices.length,
                        varid:  csIndices.map(i => element.data.id[i])[ind].replaceAll('/', ':').replaceAll('_', ':'),
                        region_url: `/region/${pheno}/${chr}:${Math.max(pos - 200 * 1000, 0)}-${pos + 200 * 1000}`
                    });
                    
                });
            }
        })

        setLeadVariants(result);
        
    }, [data]);

    const content = leadVariants.map((element, i) => { 

        const rows: Array<string> = Object.keys(element).map(key => {
            console.log(element);
            if (key != 'region_url' && key != 'varid'){
                return `<tr key=${key}>
                        <th>${key.replaceAll('_', ' ')}:</th>
                            <td>${element[key]}</td>
                        </tr>`
            }
        });

        return (
            <div style={{marginLeft: "7px"}} key={`${element.type}-${i}-div`}>
                <ReactTooltip 
                    className="tooltip-lead-vars" 
                    id='tooltip-lead-vars' 
                    html={true} 
                    arrowColor="#F4F4F4" 
                    effect='solid'
                />
                <a href={element.region_url} key={`${element.type}-${i}-a`}>
                    <span data-tip={`<table>${rows.join("")}</table>`} 
                          data-for="tooltip-lead-vars">{element.varid}
                    </span>
                </a>
            </div>
        )}
    );

    return (
        <Fragment>
            {
                leadVariants.length > 0 && props.show ?
                <Fragment>
                  <div className="flex-row-container"> Lead variants: {
                    content.flatMap((x, i) =>  i === 0 ? [x] : [(<span key={i}>,</span>), x])
                  }
		  </div>
                </Fragment> 
                : null 
            }
        </Fragment>
    )

}


export default LeadVariants;

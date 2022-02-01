import React, { useEffect } from "react";
import { Result, VariantData } from "./variantModel";
import { DataSources, Plot, populate, Data, Layouts, LayoutDataLayersEntity } from "locuszoom";
import * as d3 from "d3";

import * as LocusZoom from "locuszoom";

interface Props { variantData : VariantData }

const element_id : string = 'lz-1'

interface ResultLZ {
  id : string
  x : number
  idx : number
  pScaled : number

  phewas_code : string
  phewas_string  : string
  category_name : string
  color : string
}


const sortPhenotypes = (results : (Result & ResultLZ)[]) => {
// sort phenotypes
  if (results.every((d) => d.category_index !== undefined)) {
    results.sort((a, b) => a.category_index - b.category_index)
  } else if (results.every((d) => Number.isFinite(parseFloat(d.phenocode)) && !isNaN(parseFloat(d.phenocode)))) {
    results.sort((a, b) => parseFloat(a.phenocode) - parseFloat(b.phenocode))
  } else {
    results.sort((a, b) => a.phenocode.localeCompare(b.phenocode))
  }
}

const getFirstOfEachCategory = (results : (Result & ResultLZ)[]) => {
    const categoriesSeen = {};
    return results.filter( ( phenotype ) => {
      if(categoriesSeen.hasOwnProperty(phenotype.category)){
        return false;
      } else {
        categoriesSeen[phenotype.category] = 1;
        return true;
      }
    } )
}


const effectDirection = (parameters, input) => {
  if (typeof input == "undefined"){
    return null;
  } else if (!isNaN(input.beta)) {
    if (!isNaN(input.sebeta)) {
      if      (input.beta - 2*input.sebeta > 0) { return parameters['+'] || null; }
      else if (input.beta + 2*input.sebeta < 0) { return parameters['-'] || null; }
    } else {
      if      (input.beta > 0) { return parameters['+'] || null; }
      else if (input.beta < 0) { return parameters['-'] || null; }
    }
  } else if (!isNaN(input.or)) {
    if      (input.or > 0) { return parameters['+'] || null; }
    else if (input.or < 0) { return parameters['-'] || null; }
  }
  return null;
}

const VariantLocusZoom = ({ variantData } : Props ) => {
  useEffect(() => {
    const element = document.getElementById(element_id);
    if(variantData){
      const results : (Result & ResultLZ)[]  = JSON.parse(JSON.stringify(variantData.results))
      const firstOfEachCategory : (Result & ResultLZ)[] = getFirstOfEachCategory(results)

      const categoryOrder : { [ key : string] : number } = firstOfEachCategory.reduce((acc : { [ key : string] : number },phenotype , i : number) => { acc[phenotype.category] =i ; return acc} , {})
      results.sort((a,b) => categoryOrder[a.category] - categoryOrder[b.category])
      const uniqueCategories = [...new Set(results.map( p => p.category))];

      // https://www.d3-graph-gallery.com/graph/custom_color.html
      // https://observablehq.com/@d3/d3-scalelinear
      const colorByCategory :  d3.ScaleOrdinal<string, string> = d3.scaleOrdinal(d3.schemeCategory10).domain(uniqueCategories);
      //const colorByCategory = ((uniqueCategories.length>10) ? d3.scale.category20() : d3.scale.category10()).domain(uniqueCategories);
      results.forEach((r,i) => {
        r.phewas_code = r.phenocode
        r.phewas_string = (r.phenostring || r.phenocode)
        r.category_name = r.category
        r.color = colorByCategory(r.category)
        r.idx = i
      })

      const logLogThreshold = 1; // TODO fix this
      results.forEach((phenotype) => {
        phenotype.pScaled = phenotype.mlogp? phenotype.mlogp : -Math.log10(phenotype.pval)
        if (phenotype.pScaled > logLogThreshold) {
          phenotype.pScaled = logLogThreshold * Math.log10(phenotype.pScaled) / Math.log10(logLogThreshold)
        }
      })

      const bestNegativeLog10PValue = d3.max(results.map(function(x) { return LocusZoom.TransformationFunctions.get('neglog10')(x.pval); }));


      const PheWASSource : any = Data.PheWASSource
      PheWASSource.prototype.getData = function(state, fields, outNames, trans) {
        trans = trans || [];
        //otherwise LZ adds attributes I don't want to the original data.
        const data = results

        data.forEach((d, i) => {
          data[i]["phewas:x"] = i;
          data[i]["phewas:id"] = i.toString();
          data[i]["phewas:phenostring"] = d.phenostring
          data[i]["log_pvalue"] = d.mlogp
          trans.forEach(function(transformation, t){
            if (typeof transformation == "function"){
              data[i][outNames[t]] = transformation(data[i][fields[t]]);
            }
          });
        });
        return function(chain) {
          return {header: chain.header || {}, body: data};
        }.bind(this);
      };

      const dataSources : DataSources = new DataSources();
      dataSources.add("phewas", ['PheWASLZ', {url: '/this/is/not/used'}])

      const phewasPanel = Layouts.get("panel", "phewas",undefined);
      const sigDataLayer = phewasPanel.data_layers[0]


      const significanceThreshold = 0.05 / results.length;
      const neglog10SignificanceThreshold = -Math.log10(significanceThreshold);
      sigDataLayer.offset = neglog10SignificanceThreshold;

      sigDataLayer.tooltip = {
        //TODO: modify LZ to support tooltips on a line. right now this doesn't do anything.
        closable: true,
        html: 'foo',
        hide: { 'and': ['unhighlighted', 'unselected'] },
        show: { 'or': ['highlighted', 'selected'] }
      };

      const pValueDataLayer = phewasPanel.data_layers[1]
      pValueDataLayer.y_axis.min_extent = [0, neglog10SignificanceThreshold*1.05];
      pValueDataLayer.y_axis.upper_buffer = 0.1;
      pValueDataLayer.tooltip.html = `
      <div><strong>{{phewas_string}}</strong></div>
      <div><strong style='color:{{color}}'>{{category_name}}</strong></div>
      `
      pValueDataLayer.y_axis.field = 'pScaled';

      // -- this is where it breaks --
      const negativeLog10Handle = (x : number) => {
        let log
        if (x === 0) {
          log = bestNegativeLog10PValue * 1.1; } else {
          log = -Math.log(x) / Math.LN10;
        }
        return log;
      };
      LocusZoom.TransformationFunctions.set("negativeLog10Handle", negativeLog10Handle);
      LocusZoom.ScaleFunctions.add("effect_direction", effectDirection);

      pValueDataLayer.label.filters = [
        {field:"pval|negativeLog10Handle", operator:">", value:neglog10SignificanceThreshold * 3/4},
        {field:"pval|negativeLog10Handle", operator:">", value:bestNegativeLog10PValue / 4},
      ];

      if (results.length > 10) {
        const topMLogPValue10 = (r :  (Result & ResultLZ)[]) => {
          const mLogPValue = r.map((a) => a['mlogp']);
          mLogPValue.sort();
          return mLogPValue[10];
        }
        pValueDataLayer.label.filters.push(
          {field:"mlogp", operator:"<", value:topMLogPValue10(results)});
      }

      // Color points by category.
      pValueDataLayer.color.parameters.categories = uniqueCategories;
      pValueDataLayer.color.parameters.values = uniqueCategories.map(colorByCategory)

      // Shape points by effect direction.
      pValueDataLayer.point_shape = [
        {
          scale_function: 'effect_direction',
          parameters: {
            '+': 'triangle-up',
            '-': 'triangle-down',
          }
        },
        'circle'
      ];

      // Make points clickable
      pValueDataLayer.behaviors.onclick = [{action:"link", href:"/pheno/{{phewas_code}}"}];

      // Use categories as x ticks.
      phewasPanel.axes.x.ticks = firstOfEachCategory.map(function(pheno) {
        return {
          style: {fill: pheno.color, "font-size":"11px", "font-weight":"bold", "text-anchor":"start"},
          transform: "translate(15, 0) rotate(50)",
          text: pheno.category,
          x: pheno.idx,
        };
      });

      const maxLogPScaled = results.reduce((acc, cur) => Math.max(acc, cur.pScaled), 0)
      const ticks = []
      let unscaled = 0
      let scaled = 0

      while (scaled < bestNegativeLog10PValue) {
        scaled = unscaled <= logLogThreshold ? unscaled : Math.round(Math.pow(logLogThreshold, unscaled/logLogThreshold))
        ticks.push({y: unscaled, text: scaled})
        unscaled += maxLogPScaled < 10 ? 1 : maxLogPScaled < 25 ? 2: 5
      }
      phewasPanel.axes.y1.ticks = ticks

      phewasPanel.axes.y1.label = '-log\u2081\u2080p-value'

      // add a little x-padding so that no points intersect the edge
      phewasPanel.x_axis.min_extent = [-1, results.length]

      const layout = {
        state: {
          variant: ['chr', 'pos', 'ref', 'alt'].map((d) => variantData.variant[d]).join("-")
        },
        dashboard: {
          components: [
            {type: "download", position: "right"}
          ]
        },
        //height: 200, // doesn't work?
        //min_height: 200
        width: 800,
        min_width: 500,
        responsive_resize: true,
        panels: [phewasPanel],
        mouse_guide: false
      }

      const plot : Plot = populate('#'+element_id, dataSources, layout);
    }
  },[variantData]);

  return <div className="variant-info col-xs-12">
      <div id={element_id}
           className="lz-locuszoom-container lz-container-responsive">
      </div>
  </div>
}

export default VariantLocusZoom
import { Column, HeaderProps, Renderer } from "react-table";
import React from "react";
import ReactDOMServer from "react-dom/server";
import { variantFromStr, variantToPheweb, variantToStr } from "./commonModel";
import { scientificFormatter, shortNumberFormatter } from "./commonFormatter";
import { LabelKeyObject , Headers } from "react-csv/components/CommonPropTypes";
import matchSorter from 'match-sorter';
import { string } from 'purify-ts';
import ReactTooltip from "react-tooltip";

interface PhewebWindow extends Window {
  release_prev: number;
}

declare let window: PhewebWindow;

// https://stackoverflow.com/questions/10463518/converting-em-to-px-in-javascript-and-getting-default-font-size
function getSize(size = '1em', parent = document.body) {
    let l = document.createElement('div')
    l.style.visibility = 'hidden'
    l.style.boxSizing = 'content-box'
    l.style.position = 'absolute'
    l.style.maxHeight = 'none'
    l.style.height = size
    parent.appendChild(l)
    const fontSize = l.clientHeight
    l.remove()
    return fontSize
}
/* React table sizes in pixels and we need to size in em to ensure the columns
 * are displayed.  Note this is height and most fonts have an aspect ratio of ~.5
 *
 */
const emsize = getSize();

export const getCounts = (arr: Array<string>) => {
  var counts = {};
  arr?.forEach(element => counts[element] = 1  + (counts[element] || 0));
  return counts
}

export const pValueSentinel = 5e-324;

const textCellFormatter : <X>( props : {value : X}) => X = (props) => props.value;
const decimalCellFormatter : <X>( props : {value : X}) => string = (props) => (+props.value).toPrecision(3);
export const optionalCellDecimalFormatter = (props) => isNaN(+props.value) || props.value === "" ? props.value : decimalCellFormatter(props);

const tofixed = (v,n) => {
    return typeof(v) == typeof(0) ? v.toFixed(n) : v
}

const numberCellFormatter = (props) : number => +props.value;
export const optionalCellNumberFormatter = (props) => isNaN(+props.value) || props.value === "" ? props.value : numberCellFormatter(props);

const scientificCellFormatter = (props) : string => (+props.value).toExponential(1);
export const optionalCellScientificFormatter = (props) => isNaN(+props.value) || props.value === "" ? props.value : scientificCellFormatter(props);

export const nearestGeneFormatter = (geneName : string | null | undefined) => {
       const geneLabels = geneName?.split(",")?.map(geneName => <a key={geneName} href={`/gene/${geneName}`}>{geneName}</a>);
       return geneLabels?[].concat(...geneLabels.map((element,i) => [<span key={i}> , </span>, element])).slice(1):<></>;
}
export const pValueCellFormatter = (props) => {
      const value = props.value;
      let result;
      if(props.value === pValueSentinel){
         result = ` << ${pValueSentinel}`
      } else if (typeof value === 'number') {
        result = value.toExponential(1)
      } else if (typeof value === 'string' && !isNaN(+props.value)) {
        result = (+value).toExponential(1)
      } else {
        result = value;
      }
      return result;
}

const betaVariantTableFormatter = (props) => {
  
  let result;

  if (isNaN(+props.value)){
    result = "NA";
  } else if (typeof props.value === 'string' && !isNaN(+props.value)){
    result =  (+props.value).toExponential(1);
  } else if (props.value === null ){
    result =  (
      <p style={{ fontWeight: 'bold', minWidth: props.width * 3, 
                  textAlign: 'center', position: 'absolute', 
                  overflow: 'overlay'}}>Not significant. Click to see stats</p>
    )
  } else {
    result = props.value;
  }
  return result
}

const stringToCount= (a) => a.split(";").filter(x=> x !== 'NA').length

const truncateString = (s,l) => {
    return s.split(";").length > l ? s.split(";").slice(0,l).join(";")+"...": s
}

const arrayCellFormatter = (props) => { return props?.value?.join(" ") || "" }

const regionBuilder = (s,r) => {
    const tmp = s.replace("chr23","chrX").replace("chr","").split("_")
    const chr=tmp[0]
    const pos_min=Math.max( parseInt( tmp[1] ) - r,1 ) //pos starts from 1
    const pos_max=parseInt( tmp[1] ) + r
    return `${chr}:${pos_min}-${pos_max}`
}

const phenotypeCellFormatter = (props) => {
  const href = `/pheno/${props.original.phenocode || props.original.pheno}`
  const label = props.value === "NA" ? props.original.pheno : props.value
  return <a href={href} target="_blank" rel="noopener noreferrer" >{label}</a>
}
const variantListCellFormatter = (prop) => {
  let cell : JSX.Element[]= []
  const variants = prop.value
  const fragments = variants.split(',').map(v => v.trim().replace(/^chr/, ''))
  for (const variantString of fragments) {
    const variant = variantFromStr(variantString)
    if(variant === undefined){
      const body = <span> <span style={{ color : '#fee'}}>{variantString} &nbsp; </span> </span>
      cell.push(body)
    } else {
      const phewebVariant = variantToPheweb(variant)
      cell.push(<span> <a href={`/variant/${phewebVariant}`}>{phewebVariant}</a> &nbsp; </span>)
    }
  }
  return cell
}

const variantCell = (value : string) => {
  const variant = variantFromStr(value)
  if(variant){
    return <a href={`/variant/${variantToPheweb(variant)}`}>{variantToStr(variant)}</a>
  } else {
    return <span>{value}</span>
  }
}

interface FunctionalVariantFinnGen {
  beta : number
  pval : number
  phenocode : string
  phenostring : string
}

export const finnGenPhenotypeSubsetValues = <E extends FunctionalVariantFinnGen>(row : E[]) => {
  const values = row.filter(v => +v.pval < 1.0e-4)
  values.sort(function(pheno1, pheno2) { return naSorter(+pheno1.pval, +pheno2.pval) })
  return values;
}
const finnGenPhenotypeCell = (prop : {  value :  FunctionalVariantFinnGen[]}) => {
  const value = finnGenPhenotypeSubsetValues<FunctionalVariantFinnGen>(prop.value);
  return <table>
    <tbody>
    { value.map(finnGenPhenotypeCellRow) }
    </tbody>
  </table>
}

const finnGenPhenotypeCellRow = ({ beta , pval, phenocode, phenostring} : FunctionalVariantFinnGen) => {
  const label = phenostring && phenostring !== "" ?phenostring : phenocode
  const arrow = beta >= 0 ?
    <span style={{ color: "green", float: "left"}} className="glyphicon glyphicon-triangle-top" aria-hidden={"true"}/>
    :
    <span style={{color: "red", float: "left"}} className="glyphicon glyphicon-triangle-bottom" aria-hidden={"true"}/>
  const body = <tr className={"gene_func_var_tab"} key={phenocode}>
    <td className={"gene_func_var_row"} style={{ width : "100px"}}>
      { arrow }
      OR {scientificFormatter(beta)}<br/>
      p-val {scientificFormatter(pval)}
    </td>
    <td>
      <a style={{ color : "black"}} href={`/pheno/${phenocode}`}> { label  }</a>
    </td>
  </tr>;

  return body;
}

const formatters = {
  "text": textCellFormatter,

  "decimal": decimalCellFormatter,
  "optionalDecimal": optionalCellDecimalFormatter,

  "number": numberCellFormatter,
  "optionalNumber": optionalCellNumberFormatter,

  "scientific": scientificCellFormatter,
  "optionalScientific": optionalCellScientificFormatter,

  "pValue": pValueCellFormatter,

  "array": arrayCellFormatter,

  "phenotype": phenotypeCellFormatter
};


const variantSorter = (a, b) => {
  const v1 = a.split(":").map(e => +e);
  const v2 = b.split(":").map(e => +e);
  if (v1[0] !== v2[0]) return v1[0] > v2[0] ? 1 : -1;
  return v1[1] > v2[1] ? 1 : -1;
};

const naSorter = (a, b) => {
  a = +a;
  b = +b;
  if (isNaN(a)) {
    if (isNaN(b)) {
      return 0;
    }
    return 1;
  }
  if (isNaN(b)) {
    return -1;
  }
  return a - b;
};

const naSmallSorter = (a, b) => {
  a = +a;
  b = +b;
  if (isNaN(a)) {
    if (isNaN(b)) {
      return 0;
    }
    return -1;
  }
  if (isNaN(b)) {
    return 1;
  }
  return a - b;
};


const isString = (x : any) => (typeof x === 'string' || x instanceof String)

const numberStringSorter = (a, b) => {
  a = +a;
  b = +b;
  if(isString(a) && isString(b)){
    return (a<b?-1:(a>b?1:0));
  }

  if (isNaN(a)) {
    if (isNaN(b)) {
      return 0;
    }
    return 1;
  }
  if (isNaN(b)) {
    return -1;
  }
  return a - b;
};



const stringToCountSorter = (a, b) => {
  const c = a.split(";").filter(x => x !== "NA").length;
  const d = b.split(";").filter(x => x !== "NA").length;
  return d - c;
};

const nullToBottomSorter = (a, b, desc) => {
  /**
   * These first 3 conditions keep null values at the bottom
   */
  if (a === null && b !== null) {
    return desc ? -1 : 1;
  }

  if (a !== null && b === null) {
    return desc ? 1 : -1;
  }

  if (a === null && b === null) {
    return 0;
  }

  return a -b
}

const naToBottomSorter = (a, b, desc) => {  
  if (isNaN(a) && !isNaN(b) ) {
    return desc ? -1 : 1;
  }

  if (!isNaN(a) && isNaN(b)) {
    return desc ? 1 : -1;
  }

  if (isNaN(a) && isNaN(b)) {
    return 0;
  }

  return a -b
}



const sorters = {
  "variant": variantSorter,
  "naNumber": naSorter,
  "numberNASmall": naSmallSorter,
  "string": stringToCountSorter,
  "number" : numberStringSorter
};


const idFilter = (filter, row) => row[filter.id] <= filter.value;
const absoluteValueFilter = (filter, row) => Math.abs(row[filter.id]) > +filter.value
const numberFilter = (filter, row) => row[filter.id] > +filter.value
const numberGEFilter = (filter, row) => row[filter.id] >= +filter.value
export const wordFilter = (filter, row) => row[filter.id].toLowerCase().includes(filter.value.toLowerCase())




const filters = {
  "id": idFilter,
  "number" : absoluteValueFilter,
  "word" : wordFilter,
  "numberGE" : numberGEFilter
};

const maxTableWidth = 1600;
const columnWith = (size) => Math.min(size, size / maxTableWidth * window.innerWidth);

const phenotypeColumns = {
    
    chipPhenotype: {
      Header: () => (<span title="phenotype" style={{ textDecoration: "underline" }}>pheno</span>),
      accessor: "LONGNAME",
      filterMethod: (filter, row) => {
        const v = filter.value.split("|");
        return (v[0] === "top" ? !!row._original.is_top : true) && row[filter.id].toLowerCase().indexOf(v[1].toLowerCase()) > -1;
      },
      Filter: ({ filter, onChange }) => {
        return (<div>
          <select
            onChange={event => {
              return onChange(event.target.value + ((filter && filter.value.split("|")[1]) || ""));
            }}
            style={{ width: "100%" }}
            value={filter ? filter.value.split("|")[0] + "|" : "all|"}>
            <option value="all|">all phenos</option>
            <option value="top|">only top pheno per variant</option>
          </select><br />
          <input style={{ float: "left" }} type="text"
                 onChange={event => onChange(((filter && filter.value.split("|")[0]) || "all") + "|" + event.target.value)} />
        </div>);
      },
      Cell: phenotypeCellFormatter,
      width: columnWith(200)
    },
    chipVariant: {
      Header: () => (<span title="chr:pos:ref:alt build 38" style={{ textDecoration: "underline" }}>variant</span>),
      accessor: "variant",
      sortMethod: variantSorter,
      filterMethod: (filter, row) => {
        const s = row[filter.id].split(":");
        var v = filter.value.split("|");
        v[1] = v[1].replace("chr", "").replace("X", "23").replace(/_|-/g, ":");
        return (v[0] === "no HLA/APOE" ? !(+s[0] === 6 && +s[1] > 23000000 && +s[1] < 38000000) && !(+s[0] === 19 && +s[1] > 43000000 && +s[1] < 46000000) : true) && row[filter.id].toLowerCase().indexOf(v[1]) > -1;
      },
      Filter: ({ filter, onChange }) => {
        return (<div>
          <select
            onChange={event => {
              return onChange(event.target.value + ((filter && filter.value.split("|")[1]) || ""));
            }}
            style={{ width: "100%" }}
            value={filter ? filter.value.split("|")[0] + "|" : "all variants|"}
          >
            <option value="all variants|">all variants</option>
            <option value="no HLA/APOE|">no HLA/APOE</option>
          </select><br />
          <input style={{ float: "left", width: "140px" }} type="text"
                 onChange={event => onChange(((filter && filter.value.split("|")[0]) || "all") + "|" + event.target.value)} />
        </div>);
      },
      Cell: props => (
        <a data-html={true}
           data-tip={ReactDOMServer.renderToString(<img style={{ maxWidth: "100%", maxHeight: "100%" }}
                                                        id="cplot"
                                                        alt={props.value}
                                                        src={`/api/v1/cluster_plot/${props.value}`} />)}
           href={"https://gnomad.broadinstitute.org/variant/" + props.value.replace(/:/g, "-") + "?dataset=gnomad_r3"}
           rel="noopener noreferrer"
           target="_blank">{props.value}</a>
      ),
      width: columnWith(135)
    },
    chipRSID: {
      Header: () => (<span title="rsid" style={{ textDecoration: "underline" }}>rsid</span>),
      accessor: "rsid",
      Cell: props => props.value === "NA" ? props.value : (
        <a href={`https://www.ncbi.nlm.nih.gov/snp/{props.value}`}
           rel="noopener noreferrer"
           target="_blank">{props.value}</a>
      ),
      width: columnWith(110)
    },
    chipMostSevere: {
      Header: () => (<span title="most severe variant consequence from Variant Effect Predictor"
                           style={{ textDecoration: "underline" }}>consequence</span>),
      accessor: "most_severe",
      filterMethod: (filter, row) => {
        if (["all variants", "loss of function", "missense"].indexOf(filter.value) > -1) {
          return filter.value === "all variants" || (filter.value === "loss of function" && row[filter.id] !== "missense_variant") || (filter.value === "missense" && row[filter.id] === "missense_variant");
        } else {
          return row[filter.id].replace(/_/g, " ").indexOf(filter.value) > -1;
        }
      },
      Filter: ({ filter, onChange }) => {
        return (<div>
          <select
            onChange={event => onChange(event.target.value)}
            style={{ width: "100%" }}
            value={filter ? filter.value : "all variants"}
          >
            <option value="all variants">all variants</option>
            <option value="loss of function">loss of function</option>
            <option value="missense">missense</option>
          </select><br />
          <input style={{ float: "left", width: "140px" }} type="text"
                 onChange={event => onChange(event.target.value)} />
        </div>);
      },
      Cell: props => props.value.replace(/_/g, " ").replace(" variant", ""),
      width: columnWith(135)
    },
    chipGeneMostSevere: {
      Header: () => (<span title="gene symbol" style={{ textDecoration: "underline" }}>gene</span>),
      accessor: "gene_most_severe",
      Cell: props => (
        props.value === "NA" ? props.value :
          <a
            href={"http://www.omim.org/search/?index=entry&sort=score+desc%2C+prefix_sort+desc&start=1&limit=10&search=" + props.value}
            rel="noopener noreferrer"
            target="_blank">{props.value}</a>
      ),
      width: columnWith(80)
    },
    chipPValue: {
      Header: () => (<span title="p-value in chip EWAS" style={{ textDecoration: "underline" }}>pval</span>),
      accessor: "pval",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: pValueCellFormatter,
      width: columnWith(70)
    },
    chipPValueImputed: {
      Header: () => (
        <span title="p-value in imputed data GWAS" style={{ textDecoration: "underline" }}>pval_imp</span>),
      accessor: "pval_imp",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: optionalCellScientificFormatter,
      width: columnWith(80)
    },
    beta: {
      Header: () => (<span title="effect size beta" style={{ textDecoration: "underline" }}>beta (se)</span>),
      accessor: "beta",
      filterMethod: (filter, row) => Math.abs(row[filter.id]) > filter.value,
      Cell: optionalCellScientificFormatter,
      minWidth: 5 * emsize ,
      width: 5 * emsize
    },
    sebeta: {
      Header: () => (<span title="standard error of effect size" style={{ textDecoration: "underline" }}>sebeta</span>),
      accessor: "sebeta",
      filterMethod: (filter, row) => Math.abs(row[filter.id]) > filter.value,
      Cell: optionalCellScientificFormatter,
      minWidth: 5 * emsize ,
      width: 5 * emsize
    },
    chipBeta: {
      Header: () => (<span title="effect size beta in chip EWAS" style={{ textDecoration: "underline" }}>beta</span>),
      accessor: "beta",
      filterMethod: (filter, row) => Math.abs(row[filter.id]) > filter.value,
      Cell: optionalCellScientificFormatter,
      width: columnWith(60)
    },
    chipAF: {
      Header: () => (<span title="allele frequency (cases+controls)" style={{ textDecoration: "underline" }}>af</span>),
      accessor: "af_alt",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: optionalCellScientificFormatter,
      width: columnWith(60)
    },
    chipAFCase: {
      Header: () => (<span title="allele frequency (cases)" style={{ textDecoration: "underline" }}>af_case</span>),
      accessor: "af_alt_cases",
      filterMethod: (filter, row) =>  row[filter.id] !== null && row[filter.id] <= filter.value,
      Cell: scientificCellFormatter,
      minWidth: 5 * emsize ,
      width: 5 * emsize
    },
    chipAFControl: {
      Header: () => (<span title="allele frequency (controls)" style={{ textDecoration: "underline" }}>af_ctrl</span>),
      accessor: "af_alt_controls",
      filterMethod: (filter, row) =>  row[filter.id] !== null && row[filter.id] <= filter.value,
      Cell: scientificCellFormatter,
      minWidth: 8 * emsize ,
      width: 8 * emsize
    },
    chipAFFinn: {
      Header: () => (<span title="FIN allele frequency in gnomAD 2.0 exomes"
                           style={{ textDecoration: "underline" }}>af_FIN</span>),
      accessor: "fin_AF",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      sortMethod: naSmallSorter,
      Cell: optionalCellScientificFormatter,
      width: columnWith(60)
    },
    chipAFNFSEE: {
      Header: () => (
        <span title="NFSEE (non-Finnish-non-Swedish-non-Estonian European) allele frequency in gnomAD 2.0 exomes"
              style={{ textDecoration: "underline" }}>af_NFSEE</span>),
      accessor: "nfsee_AF",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      sortMethod: naSmallSorter,
      Cell: optionalCellScientificFormatter,
      width: columnWith(80)
    },
    chipFINEnrichment: {
      Header: () => (
        <span title="af_fin/af_nfsee in gnomAD 2 exomes" style={{ textDecoration: "underline" }}>FIN enr</span>),
      accessor: "enrichment_nfsee",
      filterMethod: (filter, row) => row[filter.id] >= filter.value,
      sortMethod: naSmallSorter,
      Cell: (props) => isNaN(+props.value) ? "NA" : props.value === 1e6 ? "inf" : Number(props.value).toPrecision(3),
      width: columnWith(60)
    },
    chipHetExCh: {
      Header: () => (<span
        title="number of heterozygotes in the 1,069 samples shared between chip and exomes: n_het_exome/n_het_chip/n_het_both_exome_and_chip"
        style={{ textDecoration: "underline" }}>het_ex_chip</span>),
      accessor: "het_ex_ch",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: textCellFormatter,
      width: columnWith(100)
    },
    chipFETPValue: {
      Header: () => (<span title="Fisher's exact p-value between allele counts on chip and all Finnish exomes"
                           style={{ textDecoration: "underline" }}>FET_p_ex</span>),
      accessor: "FET_p",
      filterMethod: (filter, row) => row[filter.id] >= filter.value,
      sortMethod: naSmallSorter,
      Cell: props => <div
        style={{ color: props.value < 1e-10 ? "rgb(224,108,117)" : props.value < 1e-5 ? "rgb(244,188,11)" : "inherit" }}>{isNaN(props.value) ? "NA" : Number(props.value).toExponential(1)}</div>,
      width: columnWith(100)
    },
    chipMissingProportion: {
      Header: () => (<span title="missing genotype proportion" style={{ textDecoration: "underline" }}>missing</span>),
      accessor: "missing_proportion",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: props => <div
        style={{ color: props.value > 0.2 ? "rgb(244,188,11)" : "inherit" }}>{props.value.toPrecision(2)}</div>,
      width: columnWith(80)
    },
    chipInfoSISU4: {
      Header: () => (<span title="INFO score based on SiSu4 imputation panel (NA if the variant is not in the panel)"
                           style={{ textDecoration: "underline" }}>INFO_imp</span>),
      accessor: "INFO_sisu4",
      filterMethod: (filter, row) => {
        if (["all variants", "in panel", "not in panel"].indexOf(filter.value) > -1) {
          return filter.value === "all variants" || (filter.value === "not in panel" && row[filter.id] === "NA") || (filter.value === "in panel" && row[filter.id] !== "NA");
        } else {
          return +row[filter.id] < +filter.value;
        }
      },
      Filter: ({ filter, onChange }) => {
        return (<div>
          <select
            onChange={event => onChange(event.target.value)}
            style={{ width: "100%" }}
            value={filter ? filter.value : "all variants"}
          >
            <option value="all variants">all variants</option>
            <option value="in panel">in panel</option>
            <option value="not in panel">not in panel</option>
          </select><br />
          <input style={{ float: "left", width: "140px" }} type="text"
                 onChange={event => onChange(event.target.value)} />
        </div>);
      },
      sortMethod: naSmallSorter,
      Cell: optionalCellDecimalFormatter,
      width: columnWith(120)
    },
    categoryIndex: {
      Header: () => (<span title="phenotype" style={{ textDecoration: "underline" }}>Category Index</span>),
      label: "category_index",
      id: "category_index",
      accessor: "category_index",
      Cell: numberCellFormatter,
      minWidth: 300
    },
    phenotype:
      {
        Header: () => (<span title="phenotype" style={{ textDecoration: "underline" }}>phenotype</span>),
        label: "phenotype",
        id: "phenotype",
        accessor: "phenostring",
        Cell: phenotypeCellFormatter,
        minWidth: 300
      },
    genePhenotype:
      {
        Header: () => (<span title="phenotype" style={{ textDecoration: "underline" }}>phenotype</span>),
        label: "phenotype",
        id: "phenotype",
        accessor: "phenostring",
        Cell: (props) => {
          const href = `/gene/${props.original.gene}/pheno/${props.original.phenocode || props.original.pheno}`
          const label = props.value === "NA" ? props.original.pheno : props.value
          return <a href={href}
                    rel="noopener noreferrer">{label}</a>
        },
        minWidth: 300
      },
    lofPhenotype: {
      Header: () => (<span title="phenotype" style={{ textDecoration: 'underline' }}>phenotype</span>),
      accessor: 'phenostring',
      Cell: props => (<a href={`/pheno/${props.original.pheno}`}
                         rel="noopener noreferrer"
                         target="_blank">{props.value}</a>),
      minWidth: 400,
    },
    geneOddRatio:
      {
        Header: () => (<span title="odds ratio" style={{ textDecoration: "underline" }}>OR</span>),
        label: "odds ratio",
        accessor: "beta",
        filterMethod: absoluteValueFilter,
        Cell: props => {
          const beta = +props.value
          const label = Math.exp(props.value).toFixed(2)
          const arrow =
            (beta >= 0) ?
              <span style={{ color: 'green', float: 'left' }} className={'glyphicon glyphicon-triangle-top'}
                    aria-hidden={'true'}>&nbsp;</span> :
              ((beta < 0) ?
                <span style={{ color: 'red', float: 'left' }} className={'glyphicon glyphicon-triangle-bottom'}
                      aria-hidden={'true'}>&nbsp;</span> :
                <span>&nbsp;</span>)

          const body = <React.Fragment>
            {arrow}
            {label}
          </React.Fragment>
          return body
        },
        minWidth: 80
      },

    risteysLink:
      {
        Header: () => (<span title="Risteys link" style={{ textDecoration: "underline" }}>Risteys</span>),
        label: "phenocode",
        accessor: "phenocode",
        Cell: props => (<a style={{
          fontSize: "1.25rem",
          padding: ".25rem .5rem",
          backgroundColor: "#2779bd",
          color: "#fff",
          borderRadius: ".25rem",
          fontWeight: 700,
          boxShadow: "0 0 5px rgba(0,0,0,.5)"
        }}
                           href={"https://risteys.finregistry.fi/phenocode/" + props.value.replace("_EXALLC", "").replace("_EXMORE", "")}>RISTEYS</a>),
        Filter: () => null,
        minWidth: emsize * 5
      },
    category:
      {
        Header: () => (<span title="phenotype category"
                             style={{ textDecoration: "underline" }}>category</span>),
        label: "category",
        accessor: "category",
        Cell: props => {
          return <span style={{ color: props.original.color || "black" }}>{props.value}</span>
        },
        minWidth: 200
      },

    numCases:
      {
        Header: () => (<span title="number of cases"
                             style={{ textDecoration: "underline" }}>number of cases</span>),
        label: "number of cases",
        accessor: "num_cases",
        Cell: props => props.value,
        filterMethod: absoluteValueFilter,
      	minWidth: 6 * emsize
      },

    numCasesPrev:
      {
        Header: () => (<span title={'number of cases previous release'}
                             style={{ textDecoration: "underline" }}>{'number of cases previous release'}</span>),
        label: 'number of cases in previous release',
        accessor: "num_cases_prev",
        Cell: props => props.value,
        filterMethod: absoluteValueFilter,
        minWidth: 50
      },

    numControls:
      {
        Header: () => (
          <span title="number of controls" style={{ textDecoration: "underline" }}>number of controls</span>),
        label: "number of controls",
        accessor: "num_controls",
        Cell: props => props.value,
        filterMethod: absoluteValueFilter,
	minWidth: 6 * emsize

      },

    numGwSignificant:
      {
        Header: () => (<span title="number of genome-wide significant hits"
                             style={{ textDecoration: "underline" }}>genome-wide sig loci</span>),
        label: "number of genome-wide significant hits",
        accessor: "num_gw_significant",
        Cell: props => props.value,
        filterMethod: absoluteValueFilter,
        minWidth: 50
      },

    numGwSignificantPrev:
      { Header: () => (<span title={"number of genome-wide significant hits release"}
                             style={{ textDecoration: "underline" }}>genome-wide sig loci previous release</span>),
        label: `number of genome-wide significant hits previous release`,
        accessor: "num_gw_significant_prev",
        Cell: props => props.value,
        filterMethod: absoluteValueFilter,
        minWidth: 50
      },

    controlLambda:
      {
        Header: () => (<span title="genomic control lambda 0.5"
                             style={{ textDecoration: "underline" }}>genomic control lambda</span>),
        label: "genomic control lambda 0.5",
        accessor: "lambda",
        Cell: props => props.value,
        filterMethod: absoluteValueFilter,
        minWidth: 50
      },

    ATCCode:
      {
        Header: () => (<span title="ATC code" style={{ textDecoration: "underline" }}>ATC code</span>),
        label: "ATC code",
        accessor: "atc",
        Cell: props => (
          <a href={`https://www.whocc.no/atc_ddd_index/?code=${props.value}`}
             rel="noopener noreferrer"
             target="_blank">{props.value}</a>),
        minWidth: 200
      },

    numSamples:
      {
        Header: () => (
          <span title="number of samples" style={{ textDecoration: "underline" }}>number of individuals with &gt; 0 purchases</span>),
        label: "number of samples",
        accessor: "num_samples",
        Cell: props => props.value,
        filterMethod: absoluteValueFilter,
        minWidth: 100
      },

    numEvents:
      {
        Header: () => (
          <span title="number of purchases" style={{ textDecoration: "underline" }}>number of purchases</span>),
        label: "number of purchases",
        accessor: "num_events",
        Cell: props => props.value,
        filterMethod: absoluteValueFilter,
        minWidth: 100
      },

    cohorts:
      {
        Header: () => (<span title="number of cohorts" style={{ textDecoration: "underline" }}>n cohorts</span>),
        label: "number of cohorts",
        accessor: "cohorts",
        Cell: props => +props.value.length,
        filterMethod: absoluteValueFilter,
        minWidth: 50
      },

    nCohorts:
      {
        Header: () => (<span title="number of cohorts" style={{ textDecoration: "underline" }}>n cohorts</span>),
        accessor: "n_cohorts",
        filterMethod: (filter, row) => row[filter.id] >= +filter.value,
        Cell: props => +props.value,
        minWidth: 80
      },

    chrom:
      {
        Header: () => (<span title="chromosome" style={{ textDecoration: "underline" }}>chr</span>),
        label: "chromosome",
        accessor: "chrom",
        Cell: props => <span style={{ float: "right", paddingRight: "10px" }}>{props.value}</span>,
        filterMethod: (filter, row) => row[filter.id] === filter.value,
        minWidth: 40
      },

    variant:
      {
        Header: () => (<span title="position in build 38" style={{ textDecoration: "underline" }}>variant</span>),
        label: "variant",
        accessor: "pos",
        Cell: props => (
          <a
            href={`/variant/${props.original.chrom}-${props.original.pos}-${props.original.ref}-${props.original.alt}`}>
            {props.original.chrom}:{props.original.pos}:{props.original.ref}:{props.original.alt}
          </a>),
        filterMethod: (filter, row) => {
          const s = filter.value.split("-").map(val => +val);
          if (s.length === 1) return row[filter.id] === filter.value;
          else if (s.length === 2) return row[filter.id] > s[0] && row[filter.id] < s[1];
        },
        minWidth: 100
      },
    pos:
      {
        Header: () => (<span title="position in build 38" style={{ textDecoration: "underline" }}>pos</span>),
        label: "position",
        accessor: "pos",
        Cell: props => (
          <a
            href={`/variant/${props.original.chrom}-${props.original.pos}-${props.original.ref}-${props.original.alt}`}>{props.value}</a>),
        filterMethod: (filter, row) => {
          const s = filter.value.split("-").map(val => +val);
          if (s.length === 1) return row[filter.id] === filter.value;
          else if (s.length === 2) return row[filter.id] > s[0] && row[filter.id] < s[1];
        },
        minWidth: 100
      },

    ref:
      {
        Header: () => (<span title="reference allele" style={{ textDecoration: "underline" }}>ref</span>),
        label: "reference allele",
        accessor: "ref",
        Cell: props => props.value,
        minWidth: 50
      },

    alt:
      {
        Header: () => (<span title="alternative allele" style={{ textDecoration: "underline" }}>alt</span>),
        label: "alternative allele",
        accessor: "alt",
        Cell: props => props.value,
        minWidth: 50
      },

    locus:
      {
        Header: () => (
          <span title="LocusZoom plot for the region" style={{ textDecoration: "underline" }}>locus</span>),
        label: "position",
        accessor: "pos",
        Cell: props => <a
          href={`/region/${props.original.phenocode}/${props.original.chrom}:${Math.max(props.original.pos - 200 * 1000, 0)}-${props.original.pos + 200 * 1000}`}>locus</a>,
        Filter: () => null,
        minWidth: 50
      },

    rsid:
      {
        Header: () => (<span title="rsid(s)" style={{ textDecoration: "underline" }}>rsid</span>),
        label: "rsid",
        accessor: "rsids",
        Cell: props => (
          <a
            href={`/variant/${props.original.chrom}-${props.original.pos}-${props.original.ref}-${props.original.alt}`}>{props.value}</a>),
	minWidth: 10 * emsize ,
	width : 10 * emsize
      },

    nearestGene:
      {
        Header: () => (<span title="nearest gene(s)" style={{ textDecoration: "underline" }}>nearest gene</span>),
        label: "nearest gene(s)",
        accessor: "nearest_genes",
        Cell: props => nearestGeneFormatter(props?.value),
        minWidth: 110
      },

    consequence:
      {
        Header: () => (<span title="VEP consequence" style={{ textDecoration: "underline" }}>consequence</span>),
        label: "VEP consequence",
        accessor: "most_severe",
        Cell: props => props.value,
        minWidth: 180
      },

    or:
      {
        Header: () => (<span title="odds ratio" style={{ textDecoration: "underline" }}>OR</span>),
        label: "odds ratio",
        accessor: "beta",
        filterMethod: absoluteValueFilter,
        Cell: props => Math.exp(props.value).toFixed(2),
        minWidth: 80
      },
      
    pValue:
      {
        Header: () => (<span title="p-value" style={{ textDecoration: "underline" }}>p-value</span>),
        accessor: "pval",
        filterMethod: (filter, row) => row[filter.id] !== null && Math.abs(row[filter.id]) < +filter.value,
        Cell: pValueCellFormatter,
	minWidth: 5 * emsize ,
        id: "pval"
      },

    infoScore:
      {
        Header: () => (<span title="INFO score" style={{ textDecoration: "underline" }}>INFO</span>),
        accessor: "info",
        filterMethod: (filter, row) => row[filter.id] >= +filter.value,
        Cell: props => isNaN(+props.value) ? "NA" : (+props.value).toPrecision(3),
        minWidth: 80
      },

    finEnrichmentText:
      {
        Header: () => (<span title="AF enrichment FIN / Non-Finnish-non-Estonian European"
                             style={{ textDecoration: "underline" }}>FIN enrichment</span>),
        accessor: "fin_enrichment",
        filterMethod: numberFilter,
        Cell: textCellFormatter,
        sortMethod: naSmallSorter,
	width : 8 * emsize ,
	minWidth: 8 * emsize
      },

    finEnrichment:
      {
        Header: () => (<span title="AF enrichment FIN / Non-Finnish-non-Estonian European"
                             style={{ textDecoration: "underline" }}>FIN enrichment</span>),
        accessor: "fin_enrichment",
        filterMethod: (filter, row) => row[filter.id] > +filter.value,
        sortMethod: naSmallSorter,
        Cell: props => {
          return isNaN(+props.value) ? "" :
            <div style={{
              color: +props.value > 5 ? "rgb(25,128,5,1)"
                : "inherit"
            }}>
              {props.value === 1e6 ? "inf" : props.value === -1 ? "NA" : Number(props.value).toPrecision(3)}
            </div>;
        },
        minWidth: 120
      },

    afUKBB:
      {
        Header: () => (<span title="allele frequency in UKBB" style={{ textDecoration: "underline" }}>af UKBB</span>),
        accessor: "maf",
        filterMethod: (filter, row) => row[filter.id] < +filter.value,
        Cell: props => (props.value === "NA" || props.value === "") ? "NA" : props.value.toPrecision(3),
        minWidth: 110
      },

    af:
      {
        Header: () => (<span title="allele frequency" style={{ textDecoration: "underline" }}>af</span>),
        accessor: "maf",
        filterMethod: (filter, row) => row[filter.id] < +filter.value,
        Cell: optionalCellDecimalFormatter,
        minWidth: 110
      },

    afCases:
      {
        Header: () => (
          <span title="allele frequency in cases" style={{ textDecoration: "underline" }}>af cases</span>),
        accessor: "maf_cases",
        filterMethod: (filter, row) => row[filter.id] < +filter.value,
        Cell: optionalCellScientificFormatter,
        minWidth: 110
      },

    afControls:
      {
        Header: () => (
          <span title="allele frequency in controls" style={{ textDecoration: "underline" }}>af controls</span>),
        accessor: "maf_controls",
        filterMethod: (filter, row) => row[filter.id] < +filter.value,
        Cell: optionalCellScientificFormatter,
        minWidth: 110
      },

    mlogp:
      {
        Header: () => (<span title="mlog" style={{ textDecoration: "underline" }}>-log10(p)</span>),
        accessor: "mlogp",
        filterMethod: (filter, row) =>  row[filter.id] !== null && row[filter.id] >= +filter.value, 
        Cell: (props) =>  isNaN(+props.value) ? "NA" : 
          typeof props.value === 'string' && !isNaN(+props.value) ? (+props.value).toPrecision(3) : 
          props.value,
        minWidth: emsize * 5,
        id: "mlogp"
      },

    UKBB:
      {
        Header: () => (<span title="UKBB Neale lab result" style={{ textDecoration: "underline" }}>UKBB</span>),
        accessor: "UKBB",
        filterMethod: (filter, row) => row[filter.id] < +filter.value,
        Cell: props => props.original.ukbb ?
          <div>{(Number(props.original.ukbb.beta) >= 0) ?
            <span style={{ color: "green", float: "left", paddingRight: "5px" }}
                  className="glyphicon glyphicon-triangle-top" aria-hidden="true">
                          &nbsp;
                    </span> :
            (Number(props.original.ukbb.beta) < 0) ?
              <span style={{ color: "red", float: "left", paddingRight: "5px" }}
                    className="glyphicon glyphicon-triangle-bottom" aria-hidden="true">
                          &nbsp;
                        </span> :
              <span>
                          &nbsp;
                        </span>} {Number(props.original.ukbb.pval).toExponential(1)}</div> : "NA",
        minWidth: 110
      },
    drugType: {
      Header: () => (<span style={{ textDecoration: "underline" }}>molecule</span>),
      accessor: "approvedName",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: textCellFormatter
    },
    targetClass: {
      Header: () => (<span style={{ textDecoration: "underline" }}>type</span>),
      accessor: "targetClass",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: arrayCellFormatter
    },
    mechanismOfAction: {
      Header: () => (<span style={{ textDecoration: "underline" }}>action</span>),
      accessor: "mechanismOfAction",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: textCellFormatter
    },
    disease: {
      Header: () => (<span style={{ textDecoration: "underline" }}>disease</span>),
      accessor: "disease",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: textCellFormatter
    },
    phase: {
      Header: () => (<span style={{ textDecoration: "underline" }}>phase</span>),
      accessor: "phase",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: textCellFormatter
    },
    drugId: {
      Header: () => (<span style={{ textDecoration: "underline" }}>id</span>),
      accessor: "drugId",
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: props => props.value === "NA" ? props.value : (
        <a href={`https://www.ebi.ac.uk/chembl/g/#search_results/all/query=${props.value}`}
           target="_blank" rel="noopener noreferrer">
          {props.value}
        </a>
      )
    },
    variants: {
      Header: () => (<span style={{ textDecoration: "underline" }}>variants</span>),
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: props => props.value === "NA" ? props.value : props.value.split(",").map(variantCell),
      accessor: "variants"
    },
    altCountCases: {
      Header: () => (<span style={{ textDecoration: "underline" }}>alt cases</span>),
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: numberCellFormatter,
      accessor: "alt_count_cases"
    },
    altCountCtrls: {
      Header: () => (<span style={{ textDecoration: "underline" }}>alt controls</span>),
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: numberCellFormatter,
      accessor: "alt_count_ctrls"
    },
    refCountCases: {
      Header: () => (<span style={{ textDecoration: "underline" }}>ref cases</span>),
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: numberCellFormatter,
      accessor: "ref_count_cases"
    },
    refCountCtrls: {
      Header: () => (<span style={{ textDecoration: "underline" }}>ref controls</span>),
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: numberCellFormatter,
      accessor: "ref_count_ctrls"
    },
    finnGenPhenotype: {
      Header: () => (<span style={{ textDecoration: "underline" }}>FinnGen phenotypes p &lt; 1E-04</span>),
      filterMethod: (filter, row) => {
          const { significant_phenos} = row;
          const labels = (significant_phenos || []).map(c => c.phenostring.toLowerCase());
          const betapval = [ ...(significant_phenos || []).map(c => c.pval),
                             ...(significant_phenos || []).map(c => c.beta)]
          const value = filter.value
          const lessThanValue = betapval.find(current => !isNaN(+current) && +current <= +value)
          const containsValue = labels.find(l => l.includes(value.toLowerCase()))
          return lessThanValue || containsValue
      },
      download : false, /* can't be downloaded as the objects will render incorrectly */
      Cell: finnGenPhenotypeCell,
      accessor: "significant_phenos"
    },
    lofGene: {
      Header: () => (<span title="gene" style={{ textDecoration: 'underline' }}>gene</span>),
      accessor: 'gene',
      Cell: props => <a href={`/gene/${props.value}`} rel="noopener noreferrer" target="_blank">{props.value}</a>,
      minWidth: 80
    },
    variantList: {
      Header: () => (<span title="variants" style={{ textDecoration: 'underline' }}>variants</span>),
      accessor: 'variants',
      Cell: variantListCellFormatter,
      minWidth: 200
    },
    referenceAlleleCaseCount: {
      Header: () => (
        <span title="reference allele count in cases" style={{ textDecoration: 'underline' }}>ref cases</span>),
      accessor: 'ref_count_cases',
      minWidth: 90,
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: props => props.value
    },
    alternativeAlleleCaseCount: {
      Header: () => (
        <span title="alternative allele count in cases" style={{ textDecoration: 'underline' }}>alt cases</span>),
      accessor: 'alt_count_cases',
      minWidth: 90,
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: props => props.value
    },
    referenceAlleleControlCount: {
      Header: () => (
        <span title="reference allele count in controls" style={{ textDecoration: 'underline' }}>ref controls</span>),
      accessor: 'ref_count_ctrls',
      minWidth: 90,
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: props => props.value
    },
    alternativeAlleleControlCount: {
      Header: () => (
        <span title="alternative allele count in controls" style={{ textDecoration: 'underline' }}>alt controls</span>),
      accessor: 'alt_count_ctrls',
      minWidth: 90,
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: props => props.value
    },
    codingPhenotype: {
      Header: () => (<span title="phenotype" style={{ textDecoration: 'underline' }}>pheno</span>),
      accessor: 'phenoname',
      filterMethod: (filter, row) => {
        var v = filter.value.split('|')
        return (v[0] === 'top' ? !!row._original.is_top : true) && row[filter.id].toLowerCase().indexOf(v[1]) > -1
      },
      Filter: ({ filter, onChange }) => {
        return (<div>
          <select
            onChange={event => {
              return onChange(event.target.value + ((filter && filter.value.split('|')[1]) || ''))
            }}
            style={{ width: "100%" }}
            value={filter ? filter.value.split('|')[0] + '|' : "all|"}
          >
            <option value="all|">all phenos</option>
            <option value="top|">only top pheno per variant</option>
          </select><br />
          <input style={{ float: 'left' }} type="text"
                 onChange={event => onChange(((filter && filter.value.split('|')[0]) || 'all') + '|' + event.target.value)} />
        </div>)
      },
      Cell: props => (<a href={"/pheno/" + props.original.pheno}
                         rel="noopener noreferrer"
                         target="_blank">{props.value === 'NA' ? props.original.pheno : props.value}</a>),
      width: Math.min(330, 330 / maxTableWidth * window.innerWidth),
    },
    codingVariant: {
      Header: () => (<span title="chr:pos:ref:alt build 38" style={{ textDecoration: 'underline' }}>variant</span>),
      accessor: 'variant',
      filterMethod: (filter, row) => {
        const s = row[filter.id].split(':')
        var v = filter.value.split('|')
        v[1] = v[1].replace('chr', '').replace('X', '23').replace(/_|-/g, ':')
        return (v[0] === 'no HLA/APOE' ? !(+s[0] === 6 && +s[1] > 23000000 && +s[1] < 38000000) && !(+s[0] === 19 && +s[1] > 43000000 && +s[1] < 46000000) : true) && row[filter.id].toLowerCase().indexOf(v[1]) > -1
      },
      Filter: ({ filter, onChange }) => {
        return (<div>
          <select
            onChange={event => {
              return onChange(event.target.value + ((filter && filter.value.split('|')[1]) || ''))
            }}
            style={{ width: "100%" }}
            value={filter ? filter.value.split('|')[0] + '|' : "all variants|"}
          >
            <option value="all variants|">all variants</option>
            <option value="no HLA/APOE|">no HLA/APOE</option>
          </select><br />
          <input style={{ float: 'left', width: '140px' }} type="text"
                 onChange={event => onChange(((filter && filter.value.split('|')[0]) || 'all') + '|' + event.target.value)} />
        </div>)
      },
      sortMethod: variantSorter,
      Cell: props => (
        <a href={"/variant/" + props.value.replace(/:/g, '-')}
           rel="noopener noreferrer"
           target="_blank">{props.value}</a>
      ),
      width: Math.min(150, 150 / maxTableWidth * window.innerWidth),
    },
    codingRSID: {
      Header: () => (<span title="rsid" style={{ textDecoration: 'underline' }}>rsid</span>),
      accessor: 'rsid',
      width: Math.min(110, 110 / maxTableWidth * window.innerWidth),
      Cell: props => (
        <a href={"/variant/" + props.original.variant.replace(/:/g, '-')}
           rel="noopener noreferrer"
           target="_blank">{props.value}</a>
      )
    },
    codingMostServe: {
      Header: () => (<span title="most severe variant consequence from Variant Effect Predictor"
                           style={{ textDecoration: 'underline' }}>consequence</span>),
      accessor: 'most_severe',
      //filterMethod: (filter, rows) => matchSorter(rows, filter.value, { keys: ['most_severe'] }),
      width: Math.min(120, 120 / maxTableWidth * window.innerWidth),
      Cell: props => props.value.replace(/_/g, ' ').replace(' variant', '')
    },
    codingVariantCategory: {
      Header: () => (
        <span title="variant category from gnomAD annotation" style={{ textDecoration: 'underline' }}>category</span>),
      accessor: 'variant_category',
      filterMethod: (filter, row) => (filter.value === "all") ? true : row[filter.id] === filter.value,
      Filter: ({ filter, onChange }) =>
        <select
          onChange={event => onChange(event.target.value)}
          style={{ width: "100%" }}
          value={filter ? filter.value : "all"}>
          <option value="all">all</option>
          <option value="pLoF">pLoF</option>
          <option value="LC">LC</option>
          <option value="inframe_indel">inframe indel</option>
          <option value="missense_variant">missense</option>
          <option value="start_lost">start lost</option>
          <option value="stop_lost">stop lost</option>
        </select>,
      Cell: props => props.value.replace(/_/g, ' ').replace(' variant', ''),
      width: Math.min(120, 120 / maxTableWidth * window.innerWidth),
    },
    codingGeneMostSevere: {
      Header: () => (<span title="gene symbol" style={{ textDecoration: 'underline' }}>gene</span>),
      accessor: 'gene_most_severe',
      width: Math.min(80, 80 / maxTableWidth * window.innerWidth),
      filterMethod: (filter, row) => row[filter.id].toLowerCase().startsWith(filter.value.toLowerCase()),
      Cell: props => (
        <a href={"/gene/" + props.value}
           target="_blank"
           rel="noopener noreferrer">{props.value}</a>
      )
    },
    codingAF: {
      Header: () => (<span title="allele frequency in FinnGen" style={{ textDecoration: 'underline' }}>af</span>),
      accessor: 'AF',
      width: Math.min(60, 60 / maxTableWidth * window.innerWidth),
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      Cell: shortNumberFormatter
    },
    codingEnrichmentNFSee: {
      Header: () => (
        <span title="af_fin/af_nfsee in gnomAD exomes (-2 when fin.AC == nfsee.AC == 0, -1 when fin.AC == fin.AN == 0)"
              style={{ textDecoration: 'underline' }}>FIN enr</span>),
      accessor: 'enrichment_nfsee',
      width: Math.min(60, 60 / maxTableWidth * window.innerWidth),
      filterMethod: (filter, row) => row[filter.id] >= filter.value,
      Cell: props => {
        const value = +props.value;
        return isNaN(value) ? '' :
          <div style={{
            color: +props.original['enrichment_nfsee'] > 5 ? 'rgb(25,128,5,1)'
              : 'inherit'
          }}>
            {value === 1e6 ? 'inf' : value.toPrecision(3)}
          </div>
      }
    },
    codingINFO: {
      Header: () => (<span title="imputation INFO score in FinnGen" style={{ textDecoration: 'underline' }}>INFO</span>),
      accessor: 'INFO',
      filterMethod: (filter, row) => row[filter.id] >= filter.value,
      width: Math.min(60, 60 / maxTableWidth * window.innerWidth),
      Cell: optionalCellScientificFormatter
    },
    finnGenBeta: {
      Header: () => (<span title="effect size beta in FinnGen" style={{ textDecoration: 'underline' }}>beta</span>),
      accessor: 'beta',
      width: Math.min(60, 60 / maxTableWidth * window.innerWidth),
      filterMethod: (filter, row) => Math.abs(row[filter.id]) > filter.value,
      Cell: optionalCellScientificFormatter
    },
    pip: {
      Header: () => (
        <span title="posterior inclusion probability in FinnGen" style={{ textDecoration: 'underline' }}>PIP</span>),
      accessor: 'pip',
      minWidth: 5 * emsize,
      filterMethod: (filter, row) => Math.abs(row[filter.id]) > filter.value,
      sortMethod: naSmallSorter,
      Cell: optionalCellScientificFormatter
    },
    finnGenRecessivePValue: {
      Header: () => (<span title="recessive p-value in FinnGen" style={{ textDecoration: 'underline' }}>rec p</span>),
      accessor: 'pval_recessive',
      width: Math.min(70, 70 / maxTableWidth * window.innerWidth),
      filterMethod: (filter, row) => row[filter.id] <= filter.value,
      sortMethod: naSorter,
      Cell: props => {
        const value = +props.value;
        return isNaN(value) ? 'NA' :
          <div style={{
            color: +props.original['pval_recessive'] < 5e-8 ? 'rgb(25,128,5,1)'
              : 'inherit'
          }}>
            {value.toExponential(1)}
          </div>
      }
    }
  ,
  finnGenDominantPValue: {
    Header: () => (<span title={'dominant p-value in FinnGen'}
                         style={{ textDecoration: 'underline' }}>dom p</span>),
    accessor: 'pval_dominant',
    width: Math.min(70, 70 / maxTableWidth * window.innerWidth),
    filterMethod: (filter, row) => row[filter.id] <= filter.value,
    sortMethod: naSorter,
    Cell: props => {
      const value = +props.value;
      return isNaN(value) ? 'NA' :
        <div style={{
          color: +props.original['pval_dominant'] < 5e-8 ? 'rgb(25,128,5,1)'
            : 'inherit'
        }}>
          {value.toExponential(1)}
        </div>
    }
  },
  recDominantLogRatio : {
  Header: () => (<span title="log10(p_rec/p_dom) in FinnGen" style={{textDecoration: 'underline'}}>rec/dom</span>),
    accessor: 'rec_dom_log_ratio',
  width: Math.min(70, 70/maxTableWidth*window.innerWidth),
  filterMethod: (filter, row) => row[filter.id] <= filter.value,
  sortMethod: naSorter,
  Cell: optionalCellScientificFormatter
  },
  finnGenAltHomozygotes : {
    Header: () => (<span title="number of alt homozygotes in FinnGen" style={{textDecoration: 'underline'}}>n hom</span>),
    accessor: 'AC_Hom',
    width: Math.min(60, 60/maxTableWidth*window.innerWidth),
    filterMethod: (filter, row) => row[filter.id] <= filter.value,
    Cell: props => props.value/2
  },
  altHomozygotes : {
    Header: () => (<span title="number of alt homozygotes in cases" style={{textDecoration: 'underline'}}>n hom cases</span>),
    accessor: 'n_hom_cases',
    width: Math.min(80, 80/maxTableWidth*window.innerWidth),
    filterMethod: (filter, row) => row[filter.id] <= filter.value,
    Cell: props => props.value
  },
  siteLinks : {
    Header: () => (<span title="links to other sites" style={{textDecoration: 'underline'}}>links</span>),
    accessor: 'grch37_locus',
    width: Math.min(60, 60/maxTableWidth*window.innerWidth),
    filterMethod: null,
    Cell: props => {
      const grch37 = props.value.replace(/:/g, '-') + '-' + props.original.variant.split(':').slice(2).join('-')
      return (
    <div>
	    <span style={{paddingRight: '5px'}}><a
        href={ /* http://${window.release_prev.toLowerCase()}.finngen.fi TODO */
               `/variant/${props.original.variant.replace(/:/g, '-')}`}
        rel="noopener noreferrer"
        target="_blank">{window.release_prev}</a></span>
      <span><a rel="noopener noreferrer"
               href={"https://gnomad.broadinstitute.org/variant/" + grch37}
               target="_blank">gn</a></span>
    </div>) }
  },

  betaVariant: {
    Header: () => (<span title="effect size beta" style={{ textDecoration: "underline" }}>beta (se)</span>),
    filterMethod: (filter, row) => row[filter.id] !== null && Math.abs(row[filter.id]) > +filter.value,
    Cell: betaVariantTableFormatter,
    sortMethod: nullToBottomSorter,
    accessor: "beta",
    id: 'beta',
    minWidth: 5 * emsize ,
    width: 5 * emsize
  }

}

const pqtColumns = {
  phenotype: {
    Header: () => (<span style={{ textDecoration: "underline" }}>phenotype</span>),
    accessor: "phenotype",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: textCellFormatter,
    minWidth: columnWith(120)
  },
  pheno: {
    Header: () => (<span style={{ textDecoration: "underline" }}>phenotype</span>),
    accessor: "phenotype1_region",
    filterMethod: (filter, row) => row[filter.id] == filter.value.pheno,
    Cell: (props : { value : any }) => (
      <a href={`/region/${props.value.pheno}/${props.value.region}`} target="_blank" rel="noopener noreferrer">{props.value.pheno}</a>
    ),
    minWidth: 150
  },
  phenotypeDescription: {
    Header: () => (<span style={{ textDecoration: "underline" }}>description</span>),
    accessor: "description",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: textCellFormatter,
    minWidth: columnWith(120)
  },

  n_colocs : {
    Header: () => (<span style={{ textDecoration: "underline" }}>n colocalizations</span>),
    accessor: "n_colocs",
    Cell: (e) => {
      var data = e.original.disease_colocalizations;
      var arr = data.map(element => { return element['source2_displayname'] }).sort();

      var posBeta = data.filter(element =>  element['beta2'] > 0).map(element => { return element['source2_displayname'] }).sort();
      var negBeta = data.filter(element =>  element['beta2'] <= 0).map(element => { return element['source2_displayname'] }).sort();

      var totalCounts = getCounts(arr);
      var pos = getCounts(posBeta);
      var neg = getCounts(negBeta);
    
      Object.keys(totalCounts).forEach(key => {
        if(!neg.hasOwnProperty(key)) {
          neg[key] = 0;
        }
        if(!pos.hasOwnProperty(key)) {
          pos[key] = 0;
        }
      })
      
      var rows = Object.keys(totalCounts).map((key, i) => { 
          return `<div style="margin-right: 20px" key=${key}> ↑${pos[key]} ↓${neg[key]} · ${key} </div>`
        }
      )
      var ncolocsTooltip = `<div>${rows.join("")}<div>`;

      return (
        <>
          <ReactTooltip
            id="tooltip-n-colocs"
            place="left" 
            arrowColor="transparent"
            html={true}
            effect="solid"
          />
          <span data-tip={ncolocsTooltip} data-for="tooltip-n-colocs">{e.value}</span>
        </>
      );
    },
  },
  pqtlTrait: {
    Header: () => (<span style={{ textDecoration: "underline" }}>trait</span>),
    accessor: "trait",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: textCellFormatter,
    minWidth: columnWith(120)
  },
  pqtlSource: {
    Header: () => (<span style={{ textDecoration: "underline" }}>source</span>),
    accessor: "source_displayname",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: textCellFormatter,
    minWidth: columnWith(200)
  },
  pqtlRegion: {
    Header: () => (<span style={{ textDecoration: "underline" }}>region</span>),
    accessor: "region",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: textCellFormatter,
    minWidth: columnWith(200)
  },
  pqtlCS: {
    Header: () => (<span style={{ textDecoration: "underline" }}>CS</span>),
    accessor: "cs",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: numberCellFormatter,
    minWidth: columnWith(80)
  },
  pqtlVar: {
    Header: () => (<span style={{ textDecoration: "underline" }}>variant</span>),
    accessor: "v",
    sortMethod: variantSorter,
    filterMethod: (filter, row) => {
      return (row[filter.id].includes(filter.value));
    },
    Filter: ({ filter, onChange }) => {
      return (<div>
        <input style={{ float: "left", width: "140px" }} type="text"
                 onChange={event => onChange(event.target.value)} />
        </div>);
    },
    Cell: textCellFormatter,
    minWidth: columnWith(200)
  },
  pqtlCSProb: {
    Header: () => (<span style={{ textDecoration: "underline" }}>CS prob</span>),
    accessor: "cs_specific_prob",
    filterMethod: (filter, row) => row[filter.id] <= filter.value,
    Cell: scientificCellFormatter,
    maxWidth: columnWith(80)
  },
  pqtlCSLogBF: {
    Header: () => (<span style={{ textDecoration: "underline" }}>CS bayes factor (log10)</span>),
    accessor: "cs_log10bf",
    filterMethod: (filter, row) => row[filter.id] >= filter.value,
    Cell: scientificCellFormatter,
    minWidth: columnWith(80)
  },
  pqtlCSMinR2: {
    Header: () => (<span style={{ textDecoration: "underline" }}>CS min r2</span>),
    accessor: "cs_min_r2",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: decimalCellFormatter,
    minWidth: columnWith(80)
  },
  pqtlColocNumber: {
    Header: () => (<span style={{ textDecoration: "underline" }}>number of disease colocalizations</span>),
    accessor: "disease_colocalizations",
    filterMethod: (filter, row) => row[filter.id] >= filter.value,    
    Cell: props => <div>{props.original.disease_colocalizations[0].length}</div>,
    minWidth: columnWith(80)
  },  
  pqtlBeta: {
    Header: () => (<span style={{ textDecoration: "underline" }}>beta</span>),
    accessor: "beta",
    filterMethod: (filter, row) => row[filter.id] >= filter.value,
    Cell: decimalCellFormatter,
    minWidth: columnWith(80)
  },
  pqtlPval: {
    Header: () => (<span style={{ textDecoration: "underline" }}>p-value</span>),
    accessor: "p",
    filterMethod: (filter, row) => row[filter.id] <= filter.value,
    Cell: pValueCellFormatter,
    minWidth: columnWith(80)
  },
  pqtlProb: {
    Header: () => (<span style={{ textDecoration: "underline" }}>CS PIP</span>),
    accessor: "prob",
    filterMethod: (filter, row) => row[filter.id] >= filter.value,
    Cell: scientificCellFormatter,
    minWidth: columnWith(80)
  },
  pqtlGeneMostSevere: {
    Header: () => (<span style={{ textDecoration: "underline" }}>gene</span>),
    accessor: "gene_most_severe",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: textCellFormatter,
    minWidth: columnWith(80)
  }
}

const colocColumns = {
  pheno: {
    Header: () => (<span style={{ textDecoration: "underline" }}>phenotype</span>),
    accessor: "phenotype1_region",
    filterMethod: (filter, row) => row[filter.id] == filter.value.pheno,
    Cell: (props : { value : any }) => (
      <a href={`/region/${props.value.pheno}/${props.value.region}`} target="_blank" rel="noopener noreferrer">{props.value.pheno}</a>
    ),
    minWidth: 150
  },
  description: {
    Header: () => (<span style={{ textDecoration: "underline" }}>description</span>),
    accessor: "phenotype1_description",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: textCellFormatter,
    minWidth: 250
  },
  source: {
    Header: () => (<span style={{ textDecoration: "underline" }}>source</span>),
    accessor: "source2_displayname",
    Cell: textCellFormatter,
    minWidth: 300
  },
  phenotype2: {
    Header: () => (<span style={{ textDecoration: "underline" }}>trait</span>),
    accessor: "phenotype2",
    Cell: textCellFormatter,
    minWidth: 100
  },
  phenotype2Description: {
    Header: () => (<span style={{ textDecoration: "underline" }}>description</span>),
    accessor: "phenotype2_description",
    Cell: textCellFormatter,
    minWidth: 100
  },
  clpp: {
    Header: () => (<span style={{ textDecoration: "underline" }}>clpp</span>),
    accessor: "clpp",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: decimalCellFormatter,
    minWidth: 80
  },
  clpa: {
    Header: () => (<span style={{ textDecoration: "underline" }}>clpa</span>),
    accessor: "clpa",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: decimalCellFormatter,
    minWidth: 80
  },
  lenInter: {
    Header: () => (<span style={{ textDecoration: "underline" }}>len intersect</span>),
    accessor: "len_inter",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: numberCellFormatter,
    minWidth: 80
  },
  lenCS1: {
    Header: () => (<span style={{ textDecoration: "underline" }}>len cs1</span>),
    accessor: "len_cs1",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: numberCellFormatter,
    minWidth: 80
  },
  lenCS2: {
    Header: () => (<span style={{ textDecoration: "underline" }}>len cs2</span>),
    accessor: "len_cs2",
    filterMethod: (filter, row) => row[filter.id] == filter.value,
    Cell: numberCellFormatter,
    minWidth: 100
  },
  beta1: {
    Header: () => (<span style={{ textDecoration: "underline" }}>beta cs1</span>),
    accessor: "beta1",
    filterMethod: (filter, row) => row[filter.id] >= filter.value,    
    Cell: decimalCellFormatter,
    minWidth: columnWith(80)
  },
  beta2: {
    Header: () => (<span style={{ textDecoration: "underline" }}>beta cs2</span>),
    accessor: "beta2",
    filterMethod: (filter, row) => row[filter.id] >= filter.value,    
    Cell: decimalCellFormatter,
    minWidth: columnWith(80)
  },
  pval1: {
    Header: () => (<span style={{ textDecoration: "underline" }}>p-value cs1</span>),
    accessor: "pval1",
    filterMethod: (filter, row) => row[filter.id] <= filter.value,    
    Cell: pValueCellFormatter,
    minWidth: columnWith(80)
  },
  pval2: {
    Header: () => (<span style={{ textDecoration: "underline" }}>p-value cs2</span>),
    accessor: "pval2",
    filterMethod: (filter, row) => row[filter.id] <= filter.value,    
    Cell: pValueCellFormatter,
    minWidth: columnWith(80)
  },
  leadingVariantCS1: {
    Header: () => (<span style={{ textDecoration: "underline" }}>lead variant cs1</span>),
    accessor: "locus_id1_chromosome",
    Cell: (props) => <div>{
      [props.original.locus_id1_chromosome, 
       props.original.locus_id1_position, 
       props.original.locus_id1_ref, 
       props.original.locus_id1_alt].join(":") 
    }</div>,
    minWidth: columnWith(120)
  },
  leadingVariantCS2: {
    Header: () => (<span style={{ textDecoration: "underline" }}>lead variant cs2</span>),
    accessor: "locus_id2_chromosome",
    Cell: (props) => <div>{
      [props.original.locus_id2_chromosome, 
       props.original.locus_id2_position, 
       props.original.locus_id2_ref, 
       props.original.locus_id2_alt].join(":") 
    }</div>,
    minWidth: columnWith(120)
  }
}

export const colocSubTable = [
  colocColumns.pheno,
  colocColumns.description,
  colocColumns.clpp,
  colocColumns.clpa,
  colocColumns.lenInter,
  colocColumns.lenCS1,
  colocColumns.lenCS2,
  colocColumns.leadingVariantCS1,
  colocColumns.leadingVariantCS2,
  colocColumns.beta1,
  colocColumns.beta2,
  colocColumns.pval1,
  colocColumns.pval2
]

export const phenoColocSubTable = [
  colocColumns.source,
  colocColumns.phenotype2,
  colocColumns.clpp,
  colocColumns.clpa,
  colocColumns.lenInter,
  colocColumns.lenCS1,
  colocColumns.lenCS2,
  { ...colocColumns.leadingVariantCS1, minWidth : 200},
  { ...colocColumns.leadingVariantCS2, minWidth : 200},
  colocColumns.beta1,
  colocColumns.beta2,
  colocColumns.pval1,
  colocColumns.pval2
]


export const genePqtlTableColumns = [
  pqtColumns.pqtlTrait,
  pqtColumns.pqtlSource,
  pqtColumns.pqtlRegion,
  pqtColumns.pqtlCS,
  pqtColumns.pqtlVar,
  pqtColumns.pqtlCSProb,
  pqtColumns.pqtlCSLogBF,
  pqtColumns.pqtlCSMinR2,
  pqtColumns.pqtlBeta,
  pqtColumns.pqtlPval,
  pqtColumns.pqtlProb,
  phenotypeColumns.codingMostServe,
  pqtColumns.pqtlGeneMostSevere,
  pqtColumns.pqtlColocNumber
]


export const geneColocTableColumns = [
  { ...pqtColumns.phenotype, minWidth : 150},
  { ...pqtColumns.phenotypeDescription, minWidth : 200},
  pqtColumns.n_colocs
]

export const geneLossOfFunctionTableColumns = [
  phenotypeColumns.phenotype,
  phenotypeColumns.variants,
  phenotypeColumns.pValue,
  phenotypeColumns.or,
  phenotypeColumns.altCountCases,
  phenotypeColumns.altCountCtrls,
  phenotypeColumns.refCountCases,
  phenotypeColumns.refCountCtrls
]


export const genePhenotypeTableColumns = [
  phenotypeColumns.rsid,
  phenotypeColumns.finEnrichmentText,
  phenotypeColumns.genePhenotype,
  phenotypeColumns.category,
  phenotypeColumns.geneOddRatio,
  { ...phenotypeColumns.sebeta, show : false},
  phenotypeColumns.mlogp,
  phenotypeColumns.pValue,
  phenotypeColumns.numCases

]

export const geneFunctionalVariantTableColumns = [
  phenotypeColumns.rsid,
  { ...phenotypeColumns.consequence, "width" : 8 * emsize , "minWidth": 8 * emsize },
  { ...phenotypeColumns.infoScore, "width" : 6 * emsize , "minWidth": 6 * emsize  },
  phenotypeColumns.finEnrichmentText,
  { ...phenotypeColumns.af, "width" : 6 * emsize , "minWidth": 6 * emsize },
  phenotypeColumns.finnGenPhenotype,

  { show : false , accessor: "phenocode" },
  { show : false , accessor: "phenostring" },

  { show : false , accessor: "n_case" },
  { show : false , accessor: "n_sample" },

  { show : false , accessor: "af_alt" },
  { show : false , accessor: "af_alt_cases" },
  { show : false , accessor: "af_alt_controls" },

  { show : false , accessor: "maf_control" },
  { show : false , accessor: "maf_case" },

  { show : false , accessor: "mlogp" },
  { ...phenotypeColumns.pValue , show : false },
  { ...phenotypeColumns.or , show : false }
]

export const geneDrugListTableColumns = [
  phenotypeColumns.drugType,
  phenotypeColumns.targetClass,
  phenotypeColumns.mechanismOfAction,
  phenotypeColumns.disease,
  phenotypeColumns.phase,
  phenotypeColumns.drugId
]

export const phenotypeListTableColumns = [
  phenotypeColumns.phenotype,
  phenotypeColumns.category,
  phenotypeColumns.numCases,
  phenotypeColumns.numControls,
  phenotypeColumns.numGwSignificant,
  phenotypeColumns.controlLambda];

export const phenotypeBinaryTableColumns = [
  phenotypeColumns.chrom,
  phenotypeColumns.pos,
  phenotypeColumns.ref,
  phenotypeColumns.alt,
  phenotypeColumns.locus,
  phenotypeColumns.rsid,
  phenotypeColumns.nearestGene,
  phenotypeColumns.consequence,
  phenotypeColumns.infoScore,
  phenotypeColumns.finEnrichment,
  phenotypeColumns.af,
  phenotypeColumns.afCases,
  phenotypeColumns.afControls,
  phenotypeColumns.or,
  phenotypeColumns.pValue,
  phenotypeColumns.mlogp,
  {...phenotypeColumns.sebeta, show:false }

]

export const phenotypeQuantitativeTableColumns = [
  phenotypeColumns.chrom,
  phenotypeColumns.pos,
  phenotypeColumns.ref,
  phenotypeColumns.alt,
  phenotypeColumns.locus,
  phenotypeColumns.rsid,
  phenotypeColumns.nearestGene,
  phenotypeColumns.consequence,
  phenotypeColumns.infoScore,
  phenotypeColumns.finEnrichment,
  phenotypeColumns.af,
  phenotypeColumns.beta,
  phenotypeColumns.pValue,
  phenotypeColumns.mlogp
]



export const chipTableColumns = [
  phenotypeColumns.chipPhenotype,
  phenotypeColumns.chipVariant,
  phenotypeColumns.chipRSID,
  phenotypeColumns.chipMostSevere,
  phenotypeColumns.chipGeneMostSevere,
  phenotypeColumns.chipPValue,
  phenotypeColumns.chipPValueImputed,
  phenotypeColumns.chipBeta,
  phenotypeColumns.chipAF,
  phenotypeColumns.chipAFCase,
  phenotypeColumns.chipAFControl,
  phenotypeColumns.chipAFFinn,
  phenotypeColumns.chipAFNFSEE,
  phenotypeColumns.chipFINEnrichment,
  phenotypeColumns.chipHetExCh,
  phenotypeColumns.chipFETPValue,
  phenotypeColumns.chipMissingProportion,
  phenotypeColumns.chipInfoSISU4
];
export const CodingTableColumns = [
  phenotypeColumns.codingPhenotype,
  phenotypeColumns.codingVariant,
  phenotypeColumns.codingRSID,
  phenotypeColumns.codingMostServe,
  phenotypeColumns.codingVariantCategory,
  phenotypeColumns.codingGeneMostSevere,
  phenotypeColumns.codingAF,
  phenotypeColumns.codingEnrichmentNFSee,
  phenotypeColumns.codingINFO,
  phenotypeColumns.pValue,
  phenotypeColumns.finnGenBeta,
  phenotypeColumns.pip,
  phenotypeColumns.finnGenRecessivePValue,
  phenotypeColumns.finnGenDominantPValue,
  phenotypeColumns.recDominantLogRatio,
  phenotypeColumns.altHomozygotes,
  phenotypeColumns.siteLinks ]

export const LOFTableColumns = [
  phenotypeColumns.lofPhenotype,
  phenotypeColumns.lofGene,
  { ...phenotypeColumns.pValue , minWidth: 70, accessor:  'p_value' },
  phenotypeColumns.variantList,
  phenotypeColumns.beta,
  phenotypeColumns.referenceAlleleCaseCount,
  phenotypeColumns.alternativeAlleleCaseCount,
  phenotypeColumns.referenceAlleleControlCount,
  phenotypeColumns.alternativeAlleleControlCount
]

export const variantTableColumns = [
  phenotypeColumns.category,
  phenotypeColumns.phenotype,
  phenotypeColumns.betaVariant,
  { ...phenotypeColumns.sebeta, show : false},
  { ...phenotypeColumns.pValue, sortMethod: nullToBottomSorter },
  { ...phenotypeColumns.mlogp, sortMethod: nullToBottomSorter },
  { ...phenotypeColumns.chipAFCase, accessor: 'maf_case', sortMethod: nullToBottomSorter },
  { ...phenotypeColumns.chipAFControl , accessor: 'maf_control', sortMethod: nullToBottomSorter },
  { ...phenotypeColumns.numCases , accessor: 'n_case' },
  { ...phenotypeColumns.numControls, accessor: 'n_control' },
  phenotypeColumns.pip
]

export const topHitTableColumns = [
  { ...phenotypeColumns.phenotype, accessor: "phenocode" },
  phenotypeColumns.variant,
  phenotypeColumns.rsid,
  phenotypeColumns.nearestGene ,
  phenotypeColumns.pValue,
  phenotypeColumns.mlogp
]


interface ColumnArchetype<E extends {}> {
  type: string,
  attributes: Column<E>
}

interface ColumnDescriptor<E extends {}> {
  title: string,
  label: string,
  accessor: keyof E,
  formatter: string,
  minWidth: number,
  sorter: string,
  filter: string
}

type ColumnConfiguration<E> = ColumnArchetype<E> | ColumnDescriptor<E>;
export type TableColumnConfiguration<E> = ColumnConfiguration<E>[] | undefined | null

export const createHeader = (title : string | null, label : string| null) => {
    const spanTitle = title || label || ""
    return <span title={spanTitle} style={{textDecoration: "underline"}}>
        {label || title}
    </span>
}
export const addHeader = (value, _createHeader = createHeader) => {
    const { title, label , ...remainder } = value;
    const doAddHeader = (title  !== undefined) || (label  !== undefined)
    const header = { ...(doAddHeader && { Header : _createHeader(title,label)}) }
    const columns = { ...remainder, ...header }
    return columns
}

const createColumn = <Type extends {}>(descriptor: ColumnConfiguration<Type>): Column<Type> => {
  let column: Column<Type>;

  if ("type" in descriptor) {
    column = {
      ...phenotypeColumns[descriptor.type],
      ...("attributes" in descriptor && addHeader(descriptor.attributes))
    };
  } else {
    const { title, label, accessor, formatter, minWidth, sorter, filter } = descriptor;
    const header: Renderer<HeaderProps<Type>> = createHeader(title,label);
    column = {
      Header : header,
      accessor: accessor,
      Cell: formatter in formatters ? formatters[formatter] : textCellFormatter,
      ...(sorter && sorter in sorters && { sortMethod: sorters[sorter] }),
      ...(filter && filter in filters && { filter: filters[filter] }),
      ...(minWidth && { minWidth })
    };
  }
  return column;
};

export const createTableColumns = <Type extends {}>(param: TableColumnConfiguration<Type>): Column<Type>[] | null =>
  (param) ? param.map(createColumn) : null

const reshape = <Type extends {}>(column: Column<Type>): LabelKeyObject => {
  let result: LabelKeyObject;
  if (typeof column.accessor == "string") {
    result = { label: column.id || column.accessor ,
               key: column.id || column.accessor };
  } else {
    throw Error(`invalid column : ${String(column.accessor)} : ${String(column.id)}`);
  }
  return result;
};

/* Filter out columns that have the optional
 * property : download = false
 */
export const filterDownload = <Type extends {}>(column: Column<Type> & { download? : boolean } ) => column?.download != false
/* Create the CSV link headers from the React Table Headers.
 */
export const createCSVLinkHeaders = <Type extends {}>(columns: (Column<Type> & { download? : boolean })[] | null): Headers =>
  columns?.filter(filterDownload<Type>)?.map(reshape<Type>) || []


export const csInsideTableCols = [
{Header: () => (<span title="Variant ID" style={{textDecoration: 'underline'}}>Variant ID</span>),
accessor: 'variant',
Cell: props => (<a href={"/variant/" +props.value.replace("chr","").replace(/_/g,"-")} target="_blank" rel="noopener noreferrer">{props.value.replace("chr","").replace(/_/g,":")}</a>),
minWidth: 60,
}, { ...phenotypeColumns.pValue , minWidth: 50,
}, { ...phenotypeColumns.mlogp , minWidth: 50,
}, {
Header: () => (<span title="effect size" style={{textDecoration: 'underline'}}>effect size</span>),
accessor: 'beta',
filterMethod: (filter, row) => Math.abs(row[filter.id]) >= +filter.value,
Cell: props => props.value,
minWidth: 50,
}, {
Header: () => (<span title="Gene" style={{textDecoration: 'underline'}}>Gene</span>),
accessor: 'most_severe_gene',
filterMethod: (filter, row) => row[filter.id] === +filter.value,
Cell: props => props.value !== "NA" ? (<a href={"/gene/" + props.value} target="_blank" rel="noopener noreferrer">{props.value}</a>):"NA",
minWidth: 50,
}, {
Header: () => (<span title="Consequence" style={{textDecoration: 'underline'}}>Consequence</span>),
accessor: 'most_severe_consequence',
filterMethod: (filter, row) => row[filter.id] === +filter.value,
Cell: props => props.value ,
minWidth: 50,
}, {
Header: () => (<span title="alternate allele frequency (alt. af)" style={{textDecoration: 'underline'}}>alt af</span>),
accessor: 'af_alt',
filterMethod: (filter, row) => Math.abs(row[filter.id]) < +filter.value,
    Cell: optionalCellScientificFormatter ,
minWidth: 40,
}, {
Header: () => (<span title="alt. af (cases)" style={{textDecoration: 'underline'}}>alt af (cases)</span>),
accessor: 'af_alt_cases',
filterMethod: (filter, row) => Math.abs(row[filter.id]) < +filter.value,
Cell: optionalCellScientificFormatter ,
minWidth: 40,
}, {
Header: () => (<span title="alt. af (controls)" style={{textDecoration: 'underline'}}>alt af (controls)</span>),
accessor: 'af_alt_controls',
filterMethod: (filter, row) => Math.abs(row[filter.id]) < +filter.value,
Cell: optionalCellScientificFormatter,
minWidth: 40,
}, {
Header: () => (<span title="INFO" style={{textDecoration: 'underline'}}>INFO</span>),
accessor: 'INFO',
filterMethod: (filter, row) => Math.abs(row[filter.id]) >= +filter.value,
Cell: optionalCellScientificFormatter,
minWidth: 40,
}, {
Header: () => (<span title="Finnish Enrichment" style={{textDecoration: 'underline'}}>Finnish enrichment</span>),
accessor: 'enrichment_nfsee',
filterMethod: (filter, row) => Math.abs(row[filter.id]) >= +filter.value,
Cell: optionalCellScientificFormatter ,
minWidth: 50,
}, {
Header: () => (<span title="Credible set PIP" style={{textDecoration: 'underline'}}>CS PIP</span>),
accessor: 'cs_prob',
filterMethod: (filter, row) => Math.abs(row[filter.id]) >= +filter.value,
sortMethod: nullToBottomSorter,
Cell: (props) => isNaN(+props.value) || props.value === "" || props.value === null ? 'NA' : decimalCellFormatter(props),
minWidth: 40
}, {
Header: () => (<span title="Functional Category" style={{textDecoration: 'underline'}}>Functional variant</span>),
accessor: 'functional_category',
filterMethod: (filter, row) => row[filter.id] === +filter.value,
Cell: props => props.value,
minWidth: 40
}, {
Header: () => (<span title="Matching trait" style={{textDecoration: 'underline'}}>Matching trait</span>),
accessor: 'trait_name',
sortMethod: stringToCountSorter,
filterMethod: (filter,row) => stringToCount(row[filter.id]) >= filter.value,
Cell: props => <div><span title={props.value}>{truncateString(props.value,2)}</span></div>,
minWidth: 40
}, {
Header: () => (<span title="R^2 to lead variant" style={{textDecoration: 'underline'}}>R^2 to lead variant</span>),
accessor: 'r2_to_lead',
Cell: (props) => isNaN(+props.original.cs_prob) || props.original.cs_prob === null ? 'NA' : decimalCellFormatter(props),
minWidth: 40
}]

export const csTableCols = [{
    Header: () => (<span title="variant with highest PIP in the credible set" style={{textDecoration: 'underline'}}>top PIP variant</span>),
    accessor: 'locus_id',
    filterMethod: (filter,rows) => {const fstr = "chr"+filter.value.replace("chr","").replace(/:/g,"_");return matchSorter(rows,fstr,{keys:[row => row[filter.id]]})},
    filterAll:true,
    Cell: props => (<a href={"/region/" + props.original.phenocode+"/"+regionBuilder(props.value,250000)} target="_blank" rel="noopener noreferrer">{props.value.replace("chr","").replace(/_/g,":")}</a>),
    minWidth: 60,
},{
    Header: () => (<span title="CS quality" style={{textDecoration: 'underline'}}>CS quality</span>),
    accessor: 'good_cs',
    filterMethod: (filter,row) => (filter.value === "true"?1:(filter.value === "false"?0:2)) === row[filter.id],
    Cell: props => String(props.value),
    minWidth: 60,
}, {
    Header: () => (<span title="chromosome" style={{textDecoration: 'underline'}}>chromosome</span>),
    accessor: 'chrom',
    filterMethod: (filter,row) => filter.value === row[filter.id],
    Cell: props => props.value,
    minWidth: 50,
}, {
  Header: () => (<span title="position" style={{textDecoration: 'underline'}}>position</span>),
  accessor: 'pos',
  filterMethod: (filter,row) => filter.value === row[filter.id],
  Cell: props => props.value,
  minWidth: 50,
}, { ...phenotypeColumns.pValue , minWidth: 50,
}, { ...phenotypeColumns.mlogp , accessor: 'lead_mlogp',  minWidth: 50,
}, {
    Header: () => (<span title="effect size (beta)" style={{textDecoration: 'underline'}}>effect size (beta)</span>),
    accessor: 'lead_beta',
    filterMethod: (filter, row) => Math.abs(row[filter.id]) >= +filter.value,
    Cell: props => tofixed(props.value,3),
    minWidth: 50,
},{
  Header: () => (<span title="standard error of effect size (sebeta)" style={{textDecoration: 'underline'}}>se effect size (sebeta)</span>),
  accessor: 'lead_sebeta',
  filterMethod: (filter, row) => Math.abs(row[filter.id]) >= +filter.value,
  Cell: props => tofixed(props.value,3),
  minWidth: 50,
  show: false
}, {
    Header: () => (<span title="Finnish Enrichment" style={{textDecoration: 'underline'}}>Finnish Enrichment</span>),
    accessor: 'lead_enrichment',
    filterMethod: (filter, row) => Math.abs(row[filter.id]) >= +filter.value,
    sortMethod: naToBottomSorter,
    Cell: props => tofixed(props.value,3),
    minWidth: 50,
},{
    Header: () => (<span title="Lead variant alternate allele frequency" style={{textDecoration: 'underline'}}>Alternate allele frequency</span>),
    accessor: 'lead_af_alt',
    filterMethod: (filter, row) => Math.abs(row[filter.id]) < +filter.value,
    Cell: props => props.value.toPrecision(3),
    minWidth: 50,
},{
    Header: () => (<span title="Lead Variant Gene" style={{textDecoration: 'underline'}}>Lead Variant Gene</span>),
    accessor: 'lead_most_severe_gene',
    filterMethod: (filter,rows) => matchSorter(rows,filter.value,{keys:[row=>row[filter.id]]}),
    filterAll: true,
    Cell: props => props.value !== "NA" ? (<a href={"/gene/" + props.value} target="_blank" rel="noopener noreferrer">{props.value}</a>):"NA",
    minWidth: 50,
}, {
    Header: () => (<span title="number of coding variants in the credible set. Tooltip shows variant name, most severe consequence, R² to lead variant" style={{textDecoration: 'underline'}}># coding in cs</span>),
    accessor: 'functional_variants_strict',
    sortMethod: stringToCountSorter,
    filterMethod: (filter,row) => stringToCount(row[filter.id]) >= filter.value,
    Cell: props => <div><span title={truncateString(props.value,4)}>{props.value.split(";").filter(x=>x!=="NA").length}</span></div>,
    minWidth: 40
}, {
    Header: () => (<span title="# Credible set variants" style={{textDecoration: 'underline'}}># credible variants</span>),
    accessor: 'cs_size',
    filterMethod: (filter,row) => row[filter.id] >= filter.value,
    sortMethod: numberStringSorter,
    Cell: props => <div><span title={truncateString(props.original.credible_set_variants,4)}>{props.value}</span></div>,
    minWidth: 50,
},{
    Header: () => (<span title="Credible set Log10 bayes factor" style={{textDecoration: 'underline'}}>Credible set bayes factor (log10)</span>),
    accessor: 'cs_log_bayes_factor',
    filterMethod: (filter, row) => Math.abs(row[filter.id]) >= +filter.value,
    Cell: props => tofixed(props.value,3),
    minWidth: 50,
}, {
    Header: () => (<span title="CS matching Traits" style={{textDecoration: 'underline'}}>CS matching Traits</span>),
    accessor: 'all_traits_strict',
    sortMethod: stringToCountSorter,
    filterMethod: (filter,row) => stringToCount(row[filter.id]) >= filter.value,
    Cell: props => <div><span title={props.value}>{props.value.split(";").filter(x=>x!=="NA").length}</span></div>,
    minWidth: 60,
}, {
    Header: () => (<span title="LD Partner matching Traits" style={{textDecoration: 'underline'}}>LD Partner Traits</span>),
    accessor: 'all_traits_relaxed',
    sortMethod: stringToCountSorter,
    filterMethod: (filter,row) => stringToCount(row[filter.id]) >= filter.value,
    Cell: props => <div><span title={props.value}>{props.value.split(";").filter(x=>x!=="NA").length}</span></div>,
    minWidth: 60,
}
]

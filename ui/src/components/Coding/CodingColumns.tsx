import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";
import { Link } from "react-router-dom";
import { Column } from "react-table";
import { createHeader, wordFilter } from "../../common/commonTableColumn";
import { ConfigurationWindow } from "../Configuration/configurationModel";
import { clusterPlotURL } from "./CodingAPI";
import CodingModel from "./CodingModel";

declare let window: ConfigurationWindow;
const risteysURLPrefix: string = window?.config?.application?.risteysURLPrefix || 'https://risteys.finregistry.fi/phenocode/';

type Row = CodingModel.Row

// genome-wide significance
const significant = (mlogp: number | null) => mlogp !== null && Math.pow(10, -mlogp) <= 5e-8

export const pValueRepr = (mlogp: number) => {
  const p = Math.pow(10, -mlogp);
  // in case of underflow build the string from mlogp
  if (p === 0) {
    const exponent = Math.ceil(mlogp);
    const digits = Math.round(100 * Math.pow(10, exponent - mlogp)) / 100;
    return `${digits}e-${exponent}`;
  }
  return p.toExponential(2);
};

const maf = (af: number | null) => af === null ? null : Math.min(af, 1 - af)

const formatConsequence = (consequence: string) => consequence.replace("_variant", "").replace(/_/g, " ")

// tips are html, column titles are plain text
const tipToTitle = (tip: string | undefined) => tip?.replace(/<br\s*\/?>/g, "\n").replace(/<[^>]+>/g, "") ?? null

/* sorting: nulls at the bottom in both directions, 'inf' as the largest value */
const toNumber = (value: number | 'inf') => value === 'inf' ? Infinity : value
export const nullLastSort = (a, b, desc: boolean) => {
  if (a === null) return b === null ? 0 : (desc ? -1 : 1);
  if (b === null) return desc ? 1 : -1;
  const x = toNumber(a), y = toNumber(b);
  return x > y ? 1 : x < y ? -1 : 0;
}
const mafSort = (a, b, desc: boolean) => nullLastSort(maf(a), maf(b), desc)

/* filters: filter.value is the text typed in the column filter */
const pValueFilter = (filter, row) => row[filter.id] !== null && Math.pow(10, -row[filter.id]) <= +filter.value
const absFilter = (filter, row) => row[filter.id] === 'inf' || (row[filter.id] !== null && Math.abs(row[filter.id]) >= +filter.value)
const mafFilter = (filter, row) => row[filter.id] !== null && maf(row[filter.id])! <= +filter.value

/**
 * Popup rendered into document.body, so the table cell
 * does not clip it. Opens on hover, or on click with openOnClick.
 */
const Popup = ({ label, content, openOnClick = false, style = {} }:
                 { label: React.ReactNode, content: React.ReactNode, openOnClick?: boolean, style?: React.CSSProperties }) => {
  const [position, setPosition] = useState<{ top: number, left: number } | null>(null);
  useEffect(() => {
    if (position === null) return;
    const close = () => setPosition(null);
    window.addEventListener("scroll", close, true);
    return () => window.removeEventListener("scroll", close, true);
  }, [position]);
  const open = (e: React.MouseEvent<HTMLSpanElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setPosition({ top: rect.bottom, left: rect.right });
  };
  const handlers = openOnClick ?
    { onClick: (e: React.MouseEvent<HTMLSpanElement>) => position === null ? open(e) : setPosition(null) } :
    { onMouseEnter: open, onMouseLeave: () => setPosition(null) };
  return <>
    <span className="popup-label" style={style} {...handlers}>{label}</span>
    {position && ReactDOM.createPortal(<div className="coding-popup" style={position}>{content}</div>, document.body)}
  </>
}

const directionArrow = (row: Row) => {
  const beta = row.beta_add ?? row.beta_chip_add;
  if (beta !== null && beta < 0) return <span style={{ color: "blue" }}>&darr;</span>;
  if (beta !== null && beta > 0) return <span style={{ color: "red" }}>&uarr;</span>;
  return <span style={{ visibility: "hidden" }}>&uarr;</span>;
}

const VariantCell = ({ value, original }: { value: string, original: Row }) =>
  original.mlogp_chip_add !== null ?
    <Popup label={value}
           style={{ textDecoration: "underline dotted" }}
           content={<img alt={`cluster plot ${value}`} className="cluster-plot" src={clusterPlotURL(value)} />} /> :
    <span title="this variant is not on chip or has not passed chip QC">{value}</span>

const PValueCell = ({ value }: { value: number | null }) =>
  <span className={significant(value) ? "" : "not-significant"}>{value === null ? "NA" : pValueRepr(value)}</span>

const betaCell = (mlogpKey: keyof Row) => ({ value, original }: { value: number | null, original: Row }) =>
  <span className={significant(original[mlogpKey] as number | null) ? "" : "not-significant"}>
    {value === null ? "NA" : value.toPrecision(3)}
  </span>

/**
 * Leads are ';' separated rows of
 * variant (chr:pos:ref:alt), mlogp, LD r2 to the coding variant, ?, AF
 */
const LeadsCell = ({ value, original }: { value: string | null, original: Row }) => {
  if (value === null) {
    return <span>NA</span>;
  }
  const compare = original.mlogp_add ?? original.mlogp_chip_add ?? 0;
  const leads = value.split(";").map((lead) => {
    const cols = lead.split(",");
    const variant = cols[0].split(":").map((f, i) => i === 0 && f === "23" ? "X" : f).join("-");
    return { variant, mlogp: Number(cols[1]), r2: cols[2], af: cols[4] };
  });
  // if the non-coding association is much stronger, warn about it
  const maxDiff = Math.max(0, ...leads.map(lead => lead.mlogp - compare));
  const color = maxDiff > 2 ? "#aa0000" : maxDiff > 0 ? "#aaaa00" : "#000000";
  const decimal = (v: string) => v === "NA" ? v : Number(v).toPrecision(3);
  const content = <div>
    <span>in this region there are variants that are <br/>stronger than the coding variant<br/>and may explain the association:</span>
    <table className="leads">
      <thead><tr><th>lead variant</th><th>p-val</th><th>LD r2 to coding</th><th>AF</th></tr></thead>
      <tbody>
        {leads.map(lead => <tr key={lead.variant}>
          <td><a target="_blank" rel="noopener noreferrer" href={`https://results.finngen.fi/variant/${lead.variant}`}>{lead.variant}</a></td>
          <td>{pValueRepr(lead.mlogp)}</td>
          <td>{decimal(lead.r2)}</td>
          <td>{decimal(lead.af)}</td>
        </tr>)}
      </tbody>
    </table>
  </div>;
  return <Popup label="click" openOnClick={true} style={{ color, cursor: "pointer" }} content={content} />;
}

const ResourcesCell = ({ original, dataset }: { original: Row, dataset: string }) => <>
  <a style={original.mlogp_add !== null ? { paddingRight: "5px" } : { paddingRight: "5px", visibility: "hidden" }}
     target="_blank" rel="noopener noreferrer"
     href={`https://results.finngen.fi/variant/${original.variant}`}>fg</a>
  <a style={{ paddingRight: "5px" }}
     target="_blank" rel="noopener noreferrer"
     href={`https://gnomad.broadinstitute.org/variant/${original.variant}?dataset=${dataset}`}>gn</a>
  <a target="_blank" rel="noopener noreferrer"
     href={`https://genetics.opentargets.org/variant/${original.variant.replace(/-/g, "_")}`}>ot</a>
</>

/* phenotype filter value: search text and only top phenotype per variant */
type PhenotypeFilterValue = { text: string, onlyTop: boolean }

const phenotypeFilter = (filter: { id: string, value?: PhenotypeFilterValue }, row) => {
  const { text = "", onlyTop = false } = filter.value ?? {};
  return (!onlyTop || row._original.is_top_pheno) &&
    (wordFilter({ id: filter.id, value: text }, row) || wordFilter({ id: "phenocode", value: text }, row._original));
}

const PhenotypeFilter = (count: number) => ({ filter, onChange }) => {
  const value: PhenotypeFilterValue = filter?.value ?? { text: "", onlyTop: false };
  return <div>
    <input value={value.text}
           placeholder={`search ${count} phenotypes`}
           style={{ width: "100%" }}
           onChange={(e) => onChange({ ...value, text: e.target.value })} />
    <label className="filter-option">
      <input type="checkbox"
             checked={value.onlyTop}
             onChange={(e) => onChange({ ...value, onlyTop: e.target.checked })} /> only top phenotype per variant
    </label>
  </div>;
}

const TextFilter = (placeholder: string) => ({ filter, onChange }) =>
  <input value={filter?.value ?? ""}
         placeholder={placeholder}
         style={{ width: "100%" }}
         onChange={(e) => onChange(e.target.value)} />

const ConsequenceFilter = (consequences: string[]) => ({ filter, onChange }) =>
  <select value={filter?.value ?? ""}
          style={{ width: "100%" }}
          onChange={(e) => onChange(e.target.value)}>
    <option value="">all</option>
    {consequences.map(consequence => <option key={consequence} value={consequence}>{formatConsequence(consequence)}</option>)}
  </select>

const OnlyChipFilter = ({ filter, onChange }) =>
  <label className="filter-option">
    <input type="checkbox"
           checked={!!filter?.value}
           onChange={(e) => onChange(e.target.checked || "")} /> only chip
  </label>

const countDistinct = (rows: Row[], key: keyof Row) => new Set(rows.map(row => row[key])).size

/**
 * Coding table columns.
 *
 * Filters that need the data (option lists, counts) are built from rows.
 *
 * @param rows table rows
 * @param tips header tips from configuration
 * @param dataset gnomAD dataset for links
 */
export const codingTableColumns = (rows: Row[], tips: { [key: string]: string }, dataset: string): Column<Row>[] => {
  const header = (label: string) => createHeader(tipToTitle(tips[label]), label);
  const consequences = Array.from(new Set(rows.map(row => row.most_severe).filter((c): c is string => c !== null))).sort();
  const numberColumn = { sortMethod: nullLastSort, minWidth: 70 };
  const pValueColumn = (label: string, accessor: keyof Row) =>
    ({ ...numberColumn, Header: header(label), accessor, Cell: PValueCell, filterMethod: pValueFilter });
  const betaColumn = (label: string, accessor: keyof Row, mlogpKey: keyof Row) =>
    ({ ...numberColumn, Header: header(label), accessor, Cell: betaCell(mlogpKey), filterMethod: absFilter });

  const columns = [
    {
      Header: header("phenotype"),
      accessor: "phenostring",
      minWidth: 250,
      Cell: ({ value, original }) => <span>
        {directionArrow(original)}
        <a target="_blank" rel="noopener noreferrer" href={`${risteysURLPrefix}${original.phenocode}`}>{value}</a>
      </span>,
      Filter: PhenotypeFilter(countDistinct(rows, "phenocode")),
      filterMethod: phenotypeFilter,
    },
    // hidden, included in the download
    { Header: "phenocode", accessor: "phenocode", show: false },
    {
      Header: header("gene"),
      accessor: "gene_most_severe",
      minWidth: 90,
      Cell: ({ value }) => value === null ? "NA" : <Link to={`/coding/gene/${value}`}>{value}</Link>,
      Filter: TextFilter("search"),
      filterMethod: wordFilter,
    },
    {
      Header: header("variant"),
      accessor: "variant",
      minWidth: 140,
      Cell: VariantCell,
      Filter: TextFilter(`search ${countDistinct(rows, "variant")} variants`),
      filterMethod: wordFilter,
    },
    {
      Header: header("rsid"),
      accessor: "rsid",
      minWidth: 100,
      Cell: ({ value }) => value ?? "NA",
      Filter: TextFilter("search"),
      filterMethod: wordFilter,
    },
    {
      Header: header("consequence"),
      accessor: "most_severe",
      minWidth: 120,
      Cell: ({ value }) => value === null ? "NA" : formatConsequence(value),
      Filter: ConsequenceFilter(consequences),
      filterMethod: (filter, row) => row[filter.id] === filter.value,
    },
    {
      Header: header("resources"),
      id: "resources",
      accessor: "variant",
      minWidth: 70,
      sortable: false,
      filterable: false,
      download: false,
      Cell: ({ original }) => <ResourcesCell original={original} dataset={dataset} />,
    },
    {
      ...numberColumn,
      Header: header("INFO"),
      accessor: "info",
      Cell: ({ value }) => value === null ? "NA" : value.toPrecision(3),
      Filter: OnlyChipFilter,
      // only chip: variants without imputation INFO
      filterMethod: (filter, row) => !filter.value || row[filter.id] === null,
    },
    {
      ...numberColumn,
      Header: header("MAF"),
      accessor: "af",
      Cell: ({ value }) => value === null ? "NA" : maf(value)!.toExponential(2),
      sortMethod: mafSort,
      filterMethod: mafFilter,
    },
    {
      ...numberColumn,
      Header: header("FIN enr."),
      accessor: "enrichment",
      Cell: ({ value }) => value === null ? "NA" : value === "inf" ? value : value.toPrecision(3),
      filterMethod: absFilter,
    },
    pValueColumn("p-val", "mlogp_add"),
    pValueColumn("p-val rec", "mlogp_chip_rec"),
    pValueColumn("p-val chip", "mlogp_chip_add"),
    betaColumn("beta", "beta_add", "mlogp_add"),
    betaColumn("beta rec", "beta_chip_rec", "mlogp_chip_rec"),
    betaColumn("beta chip", "beta_chip_add", "mlogp_chip_add"),
    {
      ...numberColumn,
      Header: header("rec-add"),
      accessor: "rec_add",
      Cell: ({ value }) => value === null ? "NA" : value.toPrecision(3),
      filterMethod: absFilter,
    },
    {
      Header: header("leads"),
      accessor: "possible_explaining_signals",
      minWidth: 60,
      sortable: false,
      filterable: false,
      Cell: LeadsCell,
    },
  ];
  return columns as Column<Row>[];
}

import React, { useEffect, useState } from "react";
import { ConfigurationWindow } from "../Configuration/configurationModel";
import { mustacheDiv } from "../../common/Utilities";
import { FunctionalVariants } from "./geneModel";
import { getGeneFunctionalVariants, getLossOfFunction } from "./geneAPI";
import { Column } from "react-table";
import { createTableColumns, geneFunctionalVariantTableColumns } from "../../common/tableColumn";
import DownloadTable, { DownloadTableProps } from "../../common/DownloadTable";
import loading from "../../common/Loading";
import { finEnrichmentLabel } from "../Finngen/gnomad";

const default_banner : string =`
<div class="row">
  <div class="col-md-10 col-lg-10 col-sm-10 col-xs-10">
    <h3>All loss of function and missense variants</h3>
  </div>
</div>
`
const default_empty: string =`                                                                                                              
    No functional or missense variants for {{gene}}                                                                                               
  `

declare let window: ConfigurationWindow;
const config = window?.config?.userInterface?.gene?.functionalVariants;
const banner: string = config?.banner || default_banner;
const empty: string = config?.empty || default_empty;

const tableColumns : Column<FunctionalVariants.ViewRow>[] = createTableColumns<FunctionalVariants.ViewRow>(config?.tableColumns) || (geneFunctionalVariantTableColumns as Column<FunctionalVariants.ViewRow>[])
const defaultSorted =[]

const tableProperties = {  defaultPageSize : 5
}
const reshapeRow = (r : FunctionalVariants.Row) : FunctionalVariants.ViewRow => {
  const rsids = r.rsids
  const alt = r.var.alt
  const chr = r.var.chr
  const pos = r.var.pos
  const ref = r.var.ref
  const most_severe = r.var.annotation.annot.most_severe.replace(/_/g, ' ').replace(' variant', '')
  const info = r.var.annotation.annot.INFO
  const maf = +r.var.annotation.annot.AF < 0.5 ? +r.var.annotation.annot.AF : 1 - +r.var.annotation.annot.AF
  const fin_enrichment = finEnrichmentLabel(r.var.annotation.gnomad)
  const significant_phenos = r.significant_phenos

  return { rsids , alt , chr , pos , ref , most_severe , info , maf , fin_enrichment , significant_phenos }
}
const dataToTableRows = (data : FunctionalVariants.Data) : FunctionalVariants.ViewRow[] => data.map(reshapeRow)

interface Props { gene : string}
const GeneFunctionalVariants = ({ gene} ) => {

  const [data, setData] = useState<FunctionalVariants.Data | null>(null);
  useEffect(() => {
    getGeneFunctionalVariants(gene,setData)
  },[]);

  const prop : DownloadTableProps<FunctionalVariants.Data, FunctionalVariants.ViewRow> = {
    tableData : data,
    dataToTableRows ,
    tableColumns ,
    tableProperties,
    defaultSorted
  }
  const context = { gene }

  let view;
  if (data == null){
    view = loading;
  } else if(dataToTableRows(data).length == 0){
    view = <div>
      {mustacheDiv(banner, context)}
      {mustacheDiv(empty, context)}

    </div>
  } else {
    view = <div>
      {mustacheDiv(banner, context)}
      <DownloadTable {...prop}/>
    </div>
  }
  return view;

}

export default GeneFunctionalVariants
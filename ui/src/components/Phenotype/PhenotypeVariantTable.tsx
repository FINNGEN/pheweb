import React, { useContext } from "react";
import { createTableColumns, phenotypeBinaryTableColumns , phenotypeQuantitativeTableColumns , pValueSentinel } from "../../common/commonTableColumn";
import { ConfigurationWindow } from "../Configuration/configurationModel";
import { Column } from "react-table";
import CommonDownloadTable, { DownloadTableProps } from "../../common/CommonDownloadTable";
import {PhenotypeVariantData, PhenotypeVariantRow, UnbinnedVariant} from "./phenotypeModel";
import { PhenotypeContext, PhenotypeState } from "./PhenotypeContext";

const defaultSorted = [{
  id: 'pval',
  desc: false
}]

const tableProperties = {
  defaultPageSize : 20,
  className : "-striped -highlight",
  defaultFilterMethod : (filter : {id : string , value : string}, row : { [ key : string ] : string }) => row[filter.id].toLowerCase().includes(filter.value.toLowerCase())
}
export const add_locus_id = (v : UnbinnedVariant) => { v.locus_id=`${v?.chrom}-${v?.pos}-${v?.ref}-${v?.alt}`; return v; }
const dataToTableRows = (data : PhenotypeVariantData| null) :  UnbinnedVariant[] => data?.unbinned_variants?.filter(v => !!v.peak).map(add_locus_id) || []
declare let window: ConfigurationWindow;

const variant = window?.config?.userInterface?.phenotype?.variant;

const quantitativeTableColumns : Column<PhenotypeVariantRow>[] = createTableColumns<PhenotypeVariantRow>(variant?.quantitative?.table?.columns) || phenotypeQuantitativeTableColumns as Column<PhenotypeVariantRow>[];
const binaryTableColumns : Column<PhenotypeVariantRow>[] = createTableColumns<PhenotypeVariantRow>(variant?.binary?.table?.columns) || phenotypeBinaryTableColumns as Column<PhenotypeVariantRow>[];

interface Props { phenotypeCode : string }
const PhenotypeVariantTable = () => {
  const { phenotype , phenotypeCode , phenotypeVariantData } = useContext<Partial<PhenotypeState>>(PhenotypeContext);
  const tableData : PhenotypeVariantData | null = phenotypeVariantData || null;
  const tableColumns = phenotype.is_binary == false?quantitativeTableColumns : binaryTableColumns;
  console.log(tableData);
  const filename : string = `${phenotypeCode}.tsv`
  const props : DownloadTableProps<PhenotypeVariantData, PhenotypeVariantRow>  = {
    filename,
    tableData,
    dataToTableRows,
    tableColumns,
    tableProperties,
    defaultSorted  }
  return <div>
    <CommonDownloadTable {...props} />
  </div>
}
export default PhenotypeVariantTable
import CommonDownloadTable, { DownloadTableProps} from "../../common/CommonDownloadTable";
import { HLAModel } from "./HLAModel";
import { hlaTableColumns } from "../../common/commonTableColumn";
import { Column } from "react-table";
import React from "react";

const tableColumns: Column<HLAModel.Row>[] = hlaTableColumns as Column<HLAModel.Row>[]

const tableProperties = {
  defaultPageSize: 30
}

const defaultSorted = [{
  id: 'phenocode',
  desc: false
},
{
  id: 'mlogp',
  desc: true
}]

const HLATable = (props) => {
  const prop: DownloadTableProps<HLAModel.Data, HLAModel.Row> = {
    filename: 'hla.tsv',
    tableData: props.data,
    dataToTableRows: (data) => data,
    tableColumns,
    tableProperties,
    defaultSorted,
  }
  return (<CommonDownloadTable {...prop} />)
}

export default HLATable;
import CommonDownloadTable, { DownloadTableProps} from "../../common/CommonDownloadTable";
import { HLAModel } from "./HLAModel";
import { hlaTableColumns } from "../../common/commonTableColumn";
import { Column } from "react-table";
import commonLoading from "../../common/CommonLoading";
import React from "react";

export const hasError = (errorMessage: string | null | undefined, content: JSX.Element): JSX.Element => {
  if (errorMessage === null || errorMessage === undefined) {
    return content
  } else {
    return <div>{errorMessage}</div>
  }
}

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
  const content = (<CommonDownloadTable {...prop} />)
  return props.data == null && props.error == null ? commonLoading : hasError(props.error, content)
}

export default HLATable;
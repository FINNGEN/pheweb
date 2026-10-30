import CommonDownloadTable, { DownloadTableProps } from "../../common/CommonDownloadTable";
import commonLoading from "../../common/CommonLoading";
import React, { useMemo } from "react";
import { CodingModel } from "./CodingModel";
import { codingTableColumns } from "./CodingColumns";

export const hasError = (errorMessage: string | null | undefined, content: JSX.Element): JSX.Element => {
  if (errorMessage === null || errorMessage === undefined) {
    return content
  } else {
    return <div>{errorMessage}</div>
  }
}

const tableProperties = {
  defaultPageSize: 30
}

const defaultSorted = [{
  id: 'mlogp_add',
  desc: true
}]

type Props = {
  data: CodingModel.Data | null
  error: string | null
  tips: { [key: string]: string }
  dataset: string
  filename?: string
}

const CodingTable = (props: Props) => {
  const rows = props.data?.results
  // filters are built from the data, so rebuild columns when it changes
  const tableColumns = useMemo(() => codingTableColumns(rows ?? [], props.tips, props.dataset),
                               [rows, props.tips, props.dataset])
  const prop: DownloadTableProps<CodingModel.Data, CodingModel.Row> = {
    filename: `${props.filename ?? 'coding.tsv'}`,
    tableData: props.data,
    dataToTableRows: (data) => data?.results ?? [],
    tableColumns,
    tableProperties,
    defaultSorted,
  }
  const content = (<CommonDownloadTable {...prop} />)
  return props.data == null && props.error == null ? commonLoading : hasError(props.error, content)
}

export default CodingTable;

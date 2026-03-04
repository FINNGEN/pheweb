import React, { useEffect, useState } from "react";
import HLAModel from "./HLAModel";
import { Column } from "react-table";
import { ConfigurationWindow } from "../Configuration/configurationModel";
import { createTableColumns, hlaTableColumns} from "../../common/commonTableColumn";
import CommonDownloadTable, { DownloadTableProps } from "../../common/CommonDownloadTable";
import commonLoading from "../../common/CommonLoading";
import ReactTable from 'react-table-v6';
import 'react-table-v6/react-table.css';
import { getTopHLAResults } from "./HLAAPI";
import { data } from "jquery";

declare let window: ConfigurationWindow;
const { config : { userInterface } = { userInterface : undefined } } = window;

const tableColumns : Column<HLAModel.Row>[] = hlaTableColumns as Column<HLAModel.Row>[]




const tableProperties = {
  defaultPageSize : 30
}

const defaultSorted = [{
  id: 'endpoint',
  desc: false
}]

const dataToTableRows = (d) => {
    console.log(d);
    return d;
}

export const hasError = (errorMessage : string | null | undefined, content:  JSX.Element) :  JSX.Element => {
  if(errorMessage === null || errorMessage === undefined){
    return content
  } else {
    return <div>{errorMessage}</div>
  }
}

const HLA = ( props ) => {

    const [ hlaData, setHlaData ] = useState<HLAModel.Data | null>(null);

    useEffect(() => {
        getTopHLAResults(setHlaData);
    }, []);

    const prop : DownloadTableProps<HLAModel.Data, HLAModel.Row> = {
        filename: 'hla.tsv',
        tableData : hlaData,
        dataToTableRows : dataToTableRows,
        tableColumns,
        tableProperties,
        defaultSorted,
    }
  const content = (
    <div> <CommonDownloadTable {...prop}/> </div>
  )
  return hlaData == null && props.error == null ? commonLoading : hasError(props.error, content)

}
export default HLA;
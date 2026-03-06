import React, { useEffect, useState } from "react";
import HLAModel from "./HLAModel";
import { Column } from "react-table";
import { ConfigurationWindow } from "../Configuration/configurationModel";
import { createTableColumns, hlaTableColumns } from "../../common/commonTableColumn";
import CommonDownloadTable, { DownloadTableProps } from "../../common/CommonDownloadTable";
import commonLoading from "../../common/CommonLoading";
import ReactTable from 'react-table-v6';
import 'react-table-v6/react-table.css';
import { getTopHLAResults, getByPhenocode, getByGene, getByVariant } from "./HLAAPI";
import { data } from "jquery";
import { RouteComponentProps } from "react-router-dom";
import Search from "./HLASearch";

declare let window: ConfigurationWindow;
const { config: { userInterface } = { userInterface: undefined } } = window;

const tableColumns: Column<HLAModel.Row>[] = hlaTableColumns as Column<HLAModel.Row>[]


//type Props = RouteComponentProps<{ phenocode : string | undefined}>

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

const dataToTableRows = (d) => {
  return d;
}

export const hasError = (errorMessage: string | null | undefined, content: JSX.Element): JSX.Element => {
  if (errorMessage === null || errorMessage === undefined) {
    return content
  } else {
    return <div>{errorMessage}</div>
  }
}

const HLA = (props) => {

  const [hlaData, setHlaData] = useState<HLAModel.Data | null>(null);

  useEffect(() => {
    console.log(props.match.path)
    if (props.match.path === '/hla/top') {
      getTopHLAResults(setHlaData);
    }
    else if (props.match.path === '/hla/phenocode/:phenocode') {
      const phenocode = props.match.params.phenocode;
      getByPhenocode(props.match.params.phenocode, setHlaData);
    }
    else if (props.match.path === '/hla/gene/:gene') {
      const gene = props.match.params.gene;
      getByGene(props.match.params.gene, setHlaData);
    }
    else if (props.match.path === '/hla/variant/:variant') {
      const alt = props.match.params.variant;
      getByVariant(props.match.params.variant, setHlaData);
    }
  }, []);

  const prop: DownloadTableProps<HLAModel.Data, HLAModel.Row> = {
    filename: 'hla.tsv',
    tableData: hlaData,
    dataToTableRows: dataToTableRows,
    tableColumns,
    tableProperties,
    defaultSorted,
  }
  const content = (
    <div>
      <Search />
      <br />
      <CommonDownloadTable {...prop} />
    </div>
  )
  return hlaData == null && props.error == null ? commonLoading : hasError(props.error, content)

}
export default HLA;
import React, { useEffect, useState } from "react";
import HLAModel from "./HLAModel";
import { Column } from "react-table";
import { ConfigurationWindow } from "../Configuration/configurationModel";
import { hlaTableColumns } from "../../common/commonTableColumn";
import CommonDownloadTable, { DownloadTableProps } from "../../common/CommonDownloadTable";
import commonLoading from "../../common/CommonLoading";
import 'react-table-v6/react-table.css';
import { getTopHLAResults, getByPhenocode, getByGene, getByVariant } from "./HLAAPI";
import Search from "./HLASearch";
import defaultConfig from "./HLAConfig";
import './style.css';
import ReactTooltip from "react-tooltip";
import HLATable from "./HLATable";

declare let window: ConfigurationWindow;
const config: { [key: string]: any } = window?.config?.userInterface?.coding?.config || defaultConfig;

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
    if (props.match.path === '/hla/top') {
      getTopHLAResults(setHlaData);
    }
    else if (props.match.path === '/hla/phenocode/:phenocode') {
      getByPhenocode(props.match.params.phenocode, setHlaData);
    }
    else if (props.match.path === '/hla/gene/:gene') {
      getByGene(props.match.params.gene, setHlaData);
    }
    else if (props.match.path === '/hla/variant/:variant') {
      getByVariant(props.match.params.variant, setHlaData);
    }
  }, []);

  const content = (
    <div className="hla">
      <div>
        <ReactTooltip place="left" arrowColor="transparent" offset={{top: -50}} html={true}/>
        <span><h2>{config.title}</h2></span>
        <span className="help" data-tip={config.help}>?</span>
      </div>
      <Search />
      <br/>
      <HLATable {...{data: hlaData}}/>
    </div>
  )
  return hlaData == null && props.error == null ? commonLoading : hasError(props.error, content)

}
export default HLA;
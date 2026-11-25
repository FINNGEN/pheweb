import React, { useEffect, useState } from "react";
import { RouteComponentProps } from "react-router-dom";
import ReactTooltip from "react-tooltip";
import 'react-table-v6/react-table.css';
import { ConfigurationWindow } from "../Configuration/configurationModel";
import { setPageTitle } from "../../common/commonUtilities";
import HelpText from "../../common/CommonHelpText";
import CodingModel, { defaultDataset } from "./CodingModel";
import { getTopResults, getByVariant, getByGene } from "./CodingAPI";
import defaultConfig from "./CodingConfig";
import Search from "./CodingSearch";
import CodingTable from "./CodingTable";
import './style.css';

declare let window: ConfigurationWindow;
const config: { [key: string]: any } = window?.config?.userInterface?.coding?.config || defaultConfig;
const dataset: string = window?.config?.userInterface?.coding?.dataset || defaultDataset;

type Props = RouteComponentProps<{ variant?: string, gene?: string }>

export const createTitle = (query: string | undefined) => query ? `coding ${query}` : 'coding';

const summary = (data: CodingModel.Data, query: string) =>
  `${query.toUpperCase()}: associations for ${new Set(data.results.map(row => row.variant)).size} coding variants`

const Coding = (props: Props) => {
  const { variant, gene } = props.match.params;
  const query = variant ?? gene;
  setPageTitle(createTitle(query));

  const [codingData, setCodingData] = useState<CodingModel.Data | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // set to false when the route changes, so responses to the previous query are ignored
    let current = true;
    setCodingData(null);
    setError(null);
    const sink = (data: CodingModel.Data) => { if (current) setCodingData(data); };
    const handler = () => (e: Error) => {
      if (current) setError(`Could not load results for ${query ?? 'top results'}: ${e.message}`);
    };
    if (variant) {
      getByVariant(variant, sink, handler);
    }
    else if (gene) {
      getByGene(gene, sink, handler);
    }
    else {
      getTopResults(sink, handler);
    }
    return () => { current = false; };
  }, [variant, gene]);

  return (
    <div className="coding">
      <div>
        <ReactTooltip place="left" arrowColor="transparent" offset={{top: -50}} html={true}/>
        <span><h2>{config.title}</h2></span>
        <HelpText text={config.help ?? defaultConfig.help} />
      </div>
      <Search />
      {codingData && <p>{query ? summary(codingData, query) : (config.top ?? defaultConfig.top)}</p>}
      <CodingTable data={codingData}
                   error={error}
                   tips={config.tip ?? defaultConfig.tip}
                   dataset={dataset}
                   filename={`coding_${query ?? 'top'}.tsv`}/>
    </div>
  );
}
export default Coding;

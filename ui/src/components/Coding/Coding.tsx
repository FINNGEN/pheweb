import React, { useEffect, useState } from "react";
import { RouteComponentProps } from "react-router-dom";
import ReactTooltip from "react-tooltip";
import 'react-table-v6/react-table.css';
import { ConfigurationWindow } from "../Configuration/configurationModel";
import { setPageTitle } from "../../common/commonUtilities";
import CodingModel, { defaultDataset } from "./CodingModel";
import { getTopResults, getByVariant, getByGene } from "./CodingAPI";
import Search, { parseQuery } from "./CodingSearch";
import defaultConfig from "./CodingConfig";
import CodingTable from "./CodingTable";
import './style.css';

declare let window: ConfigurationWindow;
const config: { [key: string]: any } = window?.config?.userInterface?.coding?.config || defaultConfig;
const dataset: string = window?.config?.userInterface?.coding?.dataset || defaultDataset;

/* query is the legacy /coding/:query route, either a variant or a gene */
type Props = RouteComponentProps<{ variant?: string, gene?: string, query?: string }>

export const createTitle = (query: string | undefined) => query ? `coding ${query}` : 'coding';

const summary = (data: CodingModel.Data, query: string) =>
  `${query.toUpperCase()}: associations for ${new Set(data.results.map(row => row.variant)).size} coding variants`

const Coding = (props: Props) => {
  const { variant, gene } = props.match.params.query ? parseQuery(props.match.params.query) : props.match.params;
  const query = variant ?? gene;
  setPageTitle(createTitle(query));

  const [codingData, setCodingData] = useState<CodingModel.Data | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setCodingData(null);
    setError(null);
    const handler = () => (e: Error) => setError(`Could not load results for ${query ?? 'top results'}: ${e.message}`);
    if (variant) {
      getByVariant(variant, setCodingData, handler);
    }
    else if (gene) {
      getByGene(gene, setCodingData, handler);
    }
    else {
      getTopResults(setCodingData, handler);
    }
  }, [variant, gene]);

  return (
    <div className="coding">
      <div>
        <ReactTooltip place="left" arrowColor="transparent" offset={{top: -50}} html={true}/>
        <span><h2>{config.title}</h2></span>
        <span className="help" data-tip={config.help}>?</span>
      </div>
      <Search isTop={query === undefined} />
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

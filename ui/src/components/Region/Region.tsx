import React from "react";
import RegionMessage from "./RegionMessage";
import RegionLocusZoom from "./RegionLocusZoom";
import RegionColocalization from "./RegionColocalization";
import RegionBanner from "./RegionBanner";
import RegionSummary from "./RegionSummary";
import RegionContextProvider, { useRegionContext } from './RegionContext';
import ColocalizationContextProvider from "./Colocalization/ColocalizationContext";
import RegionSelection from "./RegionSelection";
import { RouteComponentProps } from "react-router-dom";
import { RegionParams } from "./regionModel";
import { setPageTitle } from "../../common/commonUtilities";
import { hasError } from '../../common/CommonLoading';

type Props = RouteComponentProps<RegionParams>;

const RegionContent = () => {
  const { error } = useRegionContext();

  const content = <div>
    <RegionBanner />
    <RegionSummary />
    <RegionSelection />
    <RegionMessage />
    <div style={{ overflowX: 'auto', width: '100%' }}>
      <RegionLocusZoom />
    </div>
    <RegionColocalization />
  </div>

  return hasError(error, content);
}

const Region = (props: Props) => {
  const { locus, phenotype } = props.match.params;
  const title: string = `region ${locus} ${phenotype}`;
  setPageTitle(title);

  return (
    <RegionContextProvider params={props.match.params}>
      <ColocalizationContextProvider params={props.match.params}>
          <RegionContent/>
      </ColocalizationContextProvider>
    </RegionContextProvider>)
}

export default Region;

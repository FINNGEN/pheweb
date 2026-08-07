import React, { useContext } from "react";
import { RegionContext, RegionState } from "./RegionContext";
import { ConfigurationWindow } from '../../components/Configuration/configurationModel';
import ColocalizationList from "./Colocalization/ColocalizationList";

interface Props {};

declare let window: ConfigurationWindow;
const config = window?.config?.userInterface?.region?.colocalization;

const RegionColocalization =  (props : Props) => {
    const { region } = useContext<Partial<RegionState>>(RegionContext);


    if(config !== null && region) {
        return (<ColocalizationList filename={`${region.phenotype.phenocode}_region_${['chromosome', 'start', 'stop'].map((d) => region.region[d]).join("_")}_colocalization.tsv`} />);
    } else {
        return (<div className="col-xs-12"></div>);
    }

}

export default RegionColocalization;
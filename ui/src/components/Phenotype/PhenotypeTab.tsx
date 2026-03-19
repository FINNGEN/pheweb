import React, { useContext } from "react";
import { Tab, TabList, TabPanel, Tabs } from 'react-tabs'
import { PhenotypeContext, PhenotypeState } from "./PhenotypeContext";
import VariantTable from './PhenotypeVariantTable';
import HLATable from '../HLA/HLATable';
import PhenotypeCSTable from "./PhenotypeCSTable";
import {isNonEmptyArray} from "../../common/commonUtilities";
import ReactTooltip from "react-tooltip";
import hlaConfig from "../HLA/HLAConfig";
import InfoGlyph from "../../common/CommonInfoGlyph";

const PhenotypeTab = () => {
  const { phenotypeCode ,
          credibleSets ,
          selectedTab,
          setSelectedTab,
          hlaData } = useContext<Partial<PhenotypeState>>(PhenotypeContext);
  
  return <>
    <h3>Lead variants</h3>
    <Tabs
      forceRenderTabPanel
      selectedIndex={selectedTab}
      onSelect={setSelectedTab}
      style={{ width: '100%' }}
    >
      <TabList>
        { isNonEmptyArray(credibleSets) && <Tab>Credible Sets</Tab> }
        <Tab>Traditional</Tab>
        { isNonEmptyArray(hlaData) &&
        <Tab>Classical HLA Alleles
          <ReactTooltip place="right" arrowColor="transparent" offset={{top: -50}} html={true}/>
          <span className="help" data-tip={hlaConfig.help}> <InfoGlyph/></span>
        </Tab>
        }
      </TabList>
      { isNonEmptyArray(credibleSets) && <TabPanel>
        <div id='cs table' className='phenotype-tab'>
          <PhenotypeCSTable/>
        </div>
      </TabPanel> } 
      <TabPanel>
        <div id='traditional table' className='phenotype-tab'>
          <VariantTable/>
        </div>
      </TabPanel>
      { isNonEmptyArray(hlaData) &&
      <TabPanel>
        <div id='hla table' className='phenotype-tab'>
          <HLATable {...{data: hlaData}}/>
        </div>
      </TabPanel> }
    </Tabs>
  </>
}
export default PhenotypeTab

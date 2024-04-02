import React, { createContext, useEffect, useState } from "react";
import { GeneParams, GenePhenotypes } from "./geneModel";
import { getGenePhenotypes } from "./geneAPI";
import {setPageTitle} from "../../common/commonUtilities";

interface Props {
  readonly  children: React.ReactNode
  readonly  params : GeneParams
}

interface Parameter {
  readonly phenotype : string | null
  readonly gene : string
}

export interface GeneState {
  readonly gene : string
  readonly genePhenotype : GenePhenotypes.Data
  readonly selectedPhenotype : GenePhenotypes.Phenotype
  readonly errorMessage : string
  selectedTab : number
  setSelectedTab: React.Dispatch<React.SetStateAction<number>>
}

export const GeneContext = createContext<Partial<GeneState>>({})

export const createTitle = (gene : string, phenotype : string|undefined) => typeof phenotype === 'string'? `gene ${gene} ${phenotype}`:`gene ${gene}`;

const GeneContextProvider = ({ params : { gene , phenotype }, children } : Props) => {
  const [genePhenotype, setGenePhenotype] = useState<GenePhenotypes.Data| undefined>(undefined);
  const [selectedPhenotype, setSelectedPhenotype] = useState<GenePhenotypes.Phenotype| undefined>(undefined);
  const [errorMessage, setErrorMessage] = useState<string| undefined>(undefined);
  const [selectedTab, setSelectedTab] = useState<number>(0)

  const title : string = createTitle(gene, phenotype);
  setPageTitle(title);

  useEffect(() => { getGenePhenotypes(gene,setGenePhenotype, setErrorMessage) },[gene, setGenePhenotype]);
  useEffect(() => {
    if(genePhenotype){
      const search = genePhenotype.phenotypes.find(p => p.pheno.phenocode === phenotype)
      if(search === undefined && genePhenotype.phenotypes.length > 0){
        setSelectedPhenotype(genePhenotype.phenotypes[0]);
      } else {
        setSelectedPhenotype(search);
      }
    }
  },[genePhenotype, phenotype]);

  return (<GeneContext.Provider value={{ gene,
                                         selectedPhenotype ,
                                         genePhenotype ,
                                         errorMessage,
                                         selectedTab,
                                         setSelectedTab }}>
    { children }
  </GeneContext.Provider>)
}

export default GeneContextProvider

import React, { createContext, useEffect, useState } from "react";
import { CasualVariant, Colocalization, Locus } from "../../../common/commonModel";
import { LocusZoomData, SearchSummary } from "./ColocalizationModel";
import { getLocusZoomData, getSearchResults, getSummary } from "./ColocalizationAPI";
import { createParameter,Region, RegionParams } from "../RegionModel";
import { getRegion } from "../RegionAPI";

interface Props {
  readonly  children: React.ReactNode
  readonly params : RegionParams
}

export interface ColocalizationState {
    readonly parameter : RegionParams<Locus>
    readonly colocalization : Colocalization []
    readonly locusZoomData : LocusZoomData
    readonly searchSummary : SearchSummary
    readonly selectedColocalization : Colocalization | undefined
    readonly setSelectedColocalization : (rowid : Colocalization | undefined) => void
    readonly casualVariant : CasualVariant | undefined
    readonly selectedCasualVariant : (casualVariant : CasualVariant | undefined) => void
}

export const ColocalizationContext = createContext<Partial<ColocalizationState>>({});


export interface RegionMax {
    readonly region : Region;}

const ColocalizationContextProvider = ({ params , children} :  Props) => {

    const [colocalization, setColocalization] = useState<Colocalization[]| undefined>(undefined);
    const [locusZoomData, setLocusZoomData] = useState<LocusZoomData| undefined>(undefined);
    const [selectedColocalization, setSelectedColocalization] = useState<Colocalization | undefined>(undefined);
    const [searchSummary, setSearchSummary] = useState<SearchSummary | undefined>(undefined);
    const [casualVariant, selectedCasualVariant] = useState<CasualVariant | undefined>(undefined);
    const [maxRegion, setMaxRegion] = useState< RegionParams<Locus>| undefined>(undefined);
    const [region, setRegion] = useState<Region| undefined>(undefined); 
    
    useEffect(() => {
        const parameter : RegionParams<Locus>| undefined = createParameter(params)
        getRegion(parameter,setRegion); }, [params]);
    
    useEffect (() => {
        const locus = {
            'chromosome': region?.cond_fm_regions[1]['chr'],
            'start': region?.cond_fm_regions[1]['start'],
            'stop': region?.cond_fm_regions[1]['end']
        } 
        setMaxRegion({'locus': locus, 'phenotype': params?.phenotype})
    }, [region])


    useEffect(() => {
        const parameter : RegionParams<Locus>| undefined = createParameter(params);
        region && getSearchResults(maxRegion, setColocalization);
        getLocusZoomData(parameter, setLocusZoomData);
        getSummary(parameter, setSearchSummary);

    },[maxRegion]);
    

    const parameter : RegionParams<Locus>| undefined = createParameter(params);
    return (<ColocalizationContext.Provider value={{ parameter ,
                                                     colocalization ,
                                                     locusZoomData ,
                                                     selectedColocalization,
                                                     setSelectedColocalization,
                                                     searchSummary,
                                                     casualVariant,
                                                     selectedCasualVariant }}>
                { children }
            </ColocalizationContext.Provider>);
}

export default ColocalizationContextProvider;
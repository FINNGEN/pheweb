import React, { createContext,  useState , useEffect } from 'react';
import {CasualVariant, Colocalization, Locus, locusFromStr} from '../../../common/Model'
import {LocusZoomData, SearchResults, SearchSummary} from "./ColocalizationModel";
import {getSearchResults, getLocusZoomData, getSummary} from "./ColocalizationAPI";
import {createParameter, RegionParameter} from "../RegionModel";

interface Props { children: React.ReactNode }


export interface ColocalizationState {
    readonly parameter : RegionParameter
    readonly colocalization : Colocalization []
    readonly locusZoomData : LocusZoomData
    readonly searchSummary : SearchSummary
    readonly selectedColocalization : Colocalization | undefined
    readonly setSelectedColocalization : (rowid : Colocalization | undefined) => void
    readonly casualVariant : CasualVariant | undefined
    readonly selectedCasualVariant : (casualVariant : CasualVariant | undefined) => void
}

export const ColocalizationContext = createContext<Partial<ColocalizationState>>({});


const ColocalizationContextProvider = (props : Props) => {
    const parameter : RegionParameter| undefined = createParameter();
    const [colocalization, setColocalization] = useState<Colocalization[]| undefined>(undefined);
    const [locusZoomData, setLocusZoomData] = useState<LocusZoomData| undefined>(undefined);
    const [selectedColocalization, setSelectedColocalization] = useState<Colocalization | undefined>(undefined);
    const [searchSummary, setSearchSummary] = useState<SearchSummary | undefined>(undefined);
    const [casualVariant, selectedCasualVariant] = useState<CasualVariant | undefined>(undefined);
        useEffect(() => {
        getSearchResults(parameter, setColocalization);
        getLocusZoomData(parameter, setLocusZoomData);
        getSummary(parameter, setSearchSummary)
    },[]);

    return (<ColocalizationContext.Provider value={{ parameter ,
                                                     colocalization ,
                                                     locusZoomData ,
                                                     selectedColocalization,
                                                     setSelectedColocalization,
                                                     searchSummary,
                                                     casualVariant,
                                                     selectedCasualVariant }}>
                {props.children}
            </ColocalizationContext.Provider>);
}

export default ColocalizationContextProvider;
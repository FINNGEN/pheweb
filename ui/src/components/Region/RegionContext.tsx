import {createParameter, RegionParams, Summary} from "./regionModel";
import React, { createContext, useContext, useEffect, useState } from 'react';
import { LocusZoomContext } from "./LocusZoom/regionLocusZoomHook";
import { getRegion } from "./RegionAPI";
import { Locus } from "../../common/commonModel";

interface Props {
  readonly  children: React.ReactNode
  readonly params : RegionParams
}

export interface RegionState {
    readonly region : Summary.Region;
    readonly regionParameter : RegionParams<Locus>;
    readonly locusZoomContext : LocusZoomContext;
    readonly setLocusZoomContext : (locusZoomContext : LocusZoomContext) => void;
    readonly selectedPosition : number | undefined;
    readonly setSelectedPosition : (position : number | undefined) => void;
    readonly error : string | null;
}

export const RegionContext = createContext<Partial<RegionState>>({});

const RegionContextProvider = ({ params , children} : Props) => {
    const [region, setRegion] = useState<Summary.Region| undefined>(undefined);
    const [ locusZoomContext, setLocusZoomContext] = useState<LocusZoomContext | undefined>(undefined);
    const [ selectedPosition , setSelectedPosition] = useState<number | undefined>(undefined);
    const [error, setError] = useState<string | null>(null);

  useEffect(() => {
      const parameter : RegionParams<Locus>| undefined = createParameter(params)
      getRegion(parameter,setRegion, setError); }, [params]);
    return (<RegionContext.Provider value={{ region : region as unknown as Summary.Region,
                                             locusZoomContext,
                                             setLocusZoomContext,
                                             selectedPosition,
                                             setSelectedPosition,
                                             error }}>
        { children }
    </RegionContext.Provider>);

}
export const useRegionContext = () => useContext(RegionContext);

export default RegionContextProvider;

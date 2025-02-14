import {createParameter, RegionParams, Summary} from "./regionModel";
import React, { createContext, useEffect, useState } from "react";
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
}

export const RegionContext = createContext<Partial<RegionState>>({});

const RegionContextProvider = ({ params , children} : Props) => {
    const [region, setRegion] = useState<Summary.Region| undefined>(undefined);
    const [ locusZoomContext, setLocusZoomContext] = useState<LocusZoomContext | undefined>(undefined);
    const [ selectedPosition , setSelectedPosition] = useState<number | undefined>(undefined);
    useEffect(() => {
      const parameter : RegionParams<Locus>| undefined = createParameter(params)
      getRegion(parameter,setRegion); }, [params]);
    return (<RegionContext.Provider value={{ region : region as unknown as Summary.Region,
                                             locusZoomContext,
                                             setLocusZoomContext,
                                             selectedPosition,
                                             setSelectedPosition}}>
        { children }
    </RegionContext.Provider>);

}

export default RegionContextProvider;

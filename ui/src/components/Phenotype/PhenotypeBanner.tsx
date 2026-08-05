import { useContext } from "react";
import { isLoading } from "../../common/CommonLoading";
import { PhenotypeContext, PhenotypeState } from "./PhenotypeContext";
import React from "react";
import { risteysLinkFormatter } from "../../common/commonTableColumn";

interface Props {}

const PhenotypeBanner = (props : Props) => {
  const { phenotype } = useContext<Partial<PhenotypeState>>(PhenotypeContext);
  const content = () => (
   <div><h2 style={{marginTop: 0}}>
        {phenotype?.phenostring}
    </h2>
        <p>{phenotype?.category}</p>
   {risteysLinkFormatter(phenotype.risteysURL)}
   <table className="column_spacing">
           <tbody>
              <tr><td><b>{phenotype?.num_cases}</b> cases</td></tr>
              <tr><td><b>{phenotype?.num_controls}</b> controls</td></tr>
           </tbody>
        </table>
   </div>
  )
  return isLoading(phenotype === null || phenotype === undefined, content);
}

export default PhenotypeBanner

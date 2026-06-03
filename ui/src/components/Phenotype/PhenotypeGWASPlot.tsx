import React, { useContext, useEffect } from "react";
import { PhenotypeContext, PhenotypeState } from "./PhenotypeContext";
import { createGWASPlot } from "./phenotypeGWASD3";

const PhenotypeGWASPlot = () => {
  const { phenotypeCode, phenotypeVariantData } = useContext<Partial<PhenotypeState>>(PhenotypeContext);
  useEffect(()=> {
    phenotypeCode !== null &&
    phenotypeCode !== undefined &&
    phenotypeVariantData !== null &&
    phenotypeVariantData !== undefined &&
    createGWASPlot(phenotypeCode, phenotypeVariantData.variant_bins, phenotypeVariantData.unbinned_variants);
  }, [phenotypeCode, phenotypeVariantData])

  return (
    <div style={{ overflowX: 'auto', width: '100%' }}>
      <div id='manhattan_plot_container'/>
    </div>
  );
}

export default PhenotypeGWASPlot;
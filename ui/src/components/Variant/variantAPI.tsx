import { Ensembl, NCBI, PubMed, Variant as ModelVariant, Sumstats } from "./variantModel";
import { get, Handler } from "../../common/commonUtilities";
import { Variant, variantToPheweb } from "../../common/commonModel";
import { resolveURL } from "../Configuration/configurationModel";
import { error } from "console";

export const getVariant= (variant: Variant,
                          sink: (s: ModelVariant.Data) => void,
                          setError: (s: string | null) => void,
                          getURL = get) : void => {
  const handler : Handler = (url : string) => (e : Error) => {
    if (e.message === "NOT FOUND") {
      setError(`${variantToPheweb(variant)} not found in imputation panel or among WGS QC failed variants.`);
    } else {
      setError(`${variantToPheweb(variant)} ${e.message}`);
    }
  }
  getURL(resolveURL(`/api/variant/${variantToPheweb(variant)}`), sink,handler)
}

export  const getEnsembl = (rsid : String,
                            getURL = get<Ensembl.Data>) : Promise<Ensembl.Data | void> =>
  getURL(`https://grch37.rest.ensembl.org/variation/human/${rsid}?content-type=application/json`, x => x);


export const getNCBI = (variant: Variant,
                        sink: (s: NCBI.Data) => void,getURL = get) : void => {
  getURL(`https://www.ncbi.nlm.nih.gov/clinvar?term=${variant.chromosome}[Chromosome]%20AND%20${variant.position}[Base%20Position%20for%20Assembly%20GRCh38]`, sink)
}

export  const getPubMed = (rsid : string,
                            sink: (s: PubMed.Data) => void,getURL = get) : void => {
  getURL(`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=1&retmode=xml&term=${rsid}`, sink)
}

export const getVariantPhenotype = (variant : string, pheno: string,
                                   sink: (s: Sumstats.Data) => void,
                                   getURL = get) : void => {
                                   getURL(resolveURL(`/api/variant/${variant}/${pheno}`), sink)
}


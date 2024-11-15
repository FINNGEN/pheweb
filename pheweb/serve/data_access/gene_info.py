# -*- coding: utf-8 -*-
import abc
import requests

class GeneInfoDB(object):
    @abc.abstractmethod
    def get_gene_info(self, symbol):
        """Retrieve gene basic info given gene symbol.
        Args: symbol gene symbol
        Returns: dictionary with elements 'description': short desc, 'summary':extended summary, 'maploc':chrmaplos   'start': startpb 'stop': stopbp
        """
        raise NotImplementedError

    
class NCBIGeneInfoDao(GeneInfoDB):
    def __init__(self):
        pass

    def get_gene_info(self, symbol):
        esearch_url=f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term={symbol}[gene])%20AND%20(Homo%20sapiens[orgn])%20AND%20alive[prop]%20NOT%20newentry[gene]&sort=weight&retmode=json"
        r = requests.get(esearch_url)
        ret = r.json()["esearchresult"]
        if "ERROR" in ret:
            raise Exception(f"Error querying NCBI. Error: {ret['esearchresult']['ERROR']}")
        if ret["count"] == 0:
            raise Exception(f"Gene: {symbol} not found in NCBI db")
        id = ret["idlist"][0]
        r = requests.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id={id}&retmode=json")
        rep = r.json()
        if "result" not in rep:
            raise Exception(f"Could not access NCBI gene summary. Response: {str(rep)}")
        data = rep["result"][id]
        ## "there is a note that states chr stop seems to be missing
        ##  from top level annotation" so we will take the first in
        ### locationhist that has it.
        if "chrstop" not in data:
            locations = list(filter(lambda x: "chrstop" in  x, data["locationhist"]))
            chrstop=locations[0]["chrstop"]
        else:
            chrstop=data["chrstop"]
        
        return {
            "description": data["description"],
            "summary": data["summary"],
            "start": data["chrstart"],
            "stop": chrstop,
            "maploc": data["maplocation"],
        }

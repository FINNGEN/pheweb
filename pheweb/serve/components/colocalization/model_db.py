import abc
import attr
import typing
from pheweb.serve.data_access.db_region import MYSQLRegionDAO
from pheweb.serve.components.colocalization.model import CausalVariantVector, SearchSummary, SearchResults, PhenotypeList, ColocalizationDB, GenericArray, GenericValue, VariantVector
from pheweb.serve.models.genomics import Region 
import json
from contextlib import closing
import pymysql


def hydrate_json(v):
    index = {}
    if v["variant1"] is not None:
        for k in json.loads(v["variant1"]):
            rsid = k["rsid"]
            value = { key + '1': value for key, value in k.items() if key != "rsid" and key != "position"}
            value.update({ key + '2': None for key, value in k.items() if key != "rsid" and key != "position"})
            value["rsid"] = rsid
            value["causal_variant_id"] = rsid
            value["position"] = k["position"]
            index[rsid] = value

    if v["variant2"] is not None:
        for k in json.loads(v["variant2"]):
            rsid = k["rsid"]
            value = index.get(rsid,{ key + '1': None for key, value in k.items() if key != "rsid" and key != "position"})
            value.update({ key + '2': value for key, value in k.items() if key != "rsid" and key != "position"})
            value["rsid"] = rsid
            value["causal_variant_id"] = rsid
            value["position"] = k["position"]
            index[k["rsid"]] = value
            
    for key,value in index.items():
        if ("p1" in value and value["p1"] is not None ) and ("p2" in value and value["p2"] is not None ):
            value["membership_cs"] = "Both"
        elif "p1" in value and value["p1"] is not None:
            value["membership_cs"] = "C1"
        elif "p2" in value and value["p2"] is not None:
            value["membership_cs"] = "C2"
        else:
            value["membership_cs"] = "None"

    del(v["variant1"])
    del(v["variant2"])
    v["variants"] = list(index.values())
    return v

class ColocalizationDAO(ColocalizationDB):
    def __init__(self,
                 authentication_file : str,
                 parameters: typing.Dict[str, typing.Union[str, typing.List[str]]]):
        self._dao = MYSQLRegionDAO(authentication_file, parameters)

    def get_phenotype(self,
                      flags: typing.Dict[str, typing.Any]) -> PhenotypeList:
        """
        Return a list of phenotypes (phenotype1)
        """
        return PhenotypeList(phenotypes = [ x["phenotype"] for x in self._dao.get_phenotypes()])

    def get_locus(self,
                  phenotype: str,
                  region: Region,
                  flags: typing.Dict[str, typing.Any]) -> SearchResults:
        """
        Search for colocalization that match
        phenotype and range and return them.

        :param phenotype: phenotype to match in search
        :param chromosome_range: chromosome range to search
        :param flags: a collection of optional flags

        :return: matching colocalizations
        """
        values=self._dao.get_region(phenotype, region)
        colocalizations=[GenericValue(value = hydrate_json(v)) for v in values]
        count = len(values)
        result = SearchResults(colocalizations = colocalizations,
                               count=count)
        return result

    def get_locuszoom(self,
                      phenotype: str,
                      region: Region,
                      flags: typing.Dict[str, typing.Any]={}):
        rows={}
        values=self._dao.get_region(phenotype, region)
        values=[hydrate_json(v) for v in values]
        for r in values:
            variants = r["variants"]
            variants = map(lambda v : [
                float(v["beta1"]) if v["beta1"]   is not None else None,
                float(v["beta2"]) if v["beta2"]   is not None else None,
                int(v["cs1"])     if v["cs1"]     is not None else None,
                int(v["cs2"])     if v["cs2"]     is not None else None,
                float(v["cs_specific_prob1"]) if v["cs_specific_prob1"] is not None else None,
                float(v["cs_specific_prob2"]) if v["cs_specific_prob2"] is not None else None,
                v["low_purity1"],
                v["low_purity2"],
                float(v["p1"]) if v["p1"] is not None else None,
                float(v["p2"]) if v["p2"] is not None else None,
                float(v["se1"]) if v["se1"] is not None else None,
                float(v["se2"]) if v["se2"] is not None else None,
                v["rsid"],
                int(v["position"]),
                r["trait1"],
                r["trait2"],               
            ], variants)
            variants = list(map(list,zip(*variants)))
            if variants:
                beta1 = variants[0]
                beta2 = variants[1]
                cs1 = variants[2]
                cs2 = variants[3]
                cs_specific_prob1 = variants[4]
                cs_specific_prob2 = variants[5]
                low_purity1 = variants[6]
                low_purity2 = variants[7]
                p1 = variants[8]
                p2 = variants[9]
                se1 = variants[10]
                se2 = variants[11]
                rsid = variants[12]
                position = variants[13]
                trait1 = variants[14]
                trait2 = variants[15]
            else:
                beta1 = []
                beta2 = []
                cs1 = []
                cs2 = []
                cs_specific_prob1 = []
                cs_specific_prob2 = []
                low_purity1 = []
                low_purity2 = []
                p1 = []
                p2 = []
                se1 = []
                se2 = []
                rsid = []
                position = []
                trait1 = []
                trait2 = []
            rows[r["colocalization_id"]] = VariantVector(beta1,
                                                         beta2,
                                                         cs1,
                                                         cs2,
                                                         cs_specific_prob1,
                                                         cs_specific_prob2,
                                                         low_purity1,
                                                         low_purity2,
                                                         p1,
                                                         p2,
                                                         se1,
                                                         se2,
                                                         rsid,
                                                         position,
                                                         trait1,
                                                         trait2)
        return rows

        
    def get_locus_summary(self,
                          phenotype: str,
                          region: Region,
                          flags: typing.Dict[str, typing.Any] = {}) -> SearchSummary:
        summary = self._dao.get_region_summary(phenotype, region)[0]
        return SearchSummary(**summary)
    
    def get_colocalization(self,
                           colocalization_id : int,
                           flags : typing.Dict[str, typing.Any] = {}):
        """
        Given the identifier for a colocaliztion
        record return colocaliztion record.

        :param colocalization_id to search for
        :return: colocaliztion if one was found
        """
        with closing(self._dao.get_connection()) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                table = self._dao._parameters['colocalization_table']
                sql = f"""SELECT *
                          FROM {table}
                          where colocalization_id = %s"""
                cursor.execute(sql, [colocalization_id])
                result = GenericValue(value = hydrate_json(cursor.fetchone()))
                return result

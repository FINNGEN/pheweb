import abc
import os
import pymysql
import math
from typing import List, Dict, Union, Optional, Final
from ...load_source.load_source import load_source


class AutorepVariantDB(abc.ABC):
    @abc.abstractmethod
    def get_group_variants(self, phenotype, locus_id):
        """Retrieve a given locuses variants for a given phenotype
        Returns: A list of dictionaries. WIP
        """
        return

    @abc.abstractmethod
    def get_group_report(self, phenotype):
        """Retrieve a given phenotype's group report
        Returns: A list of dictionaries, with the group report columns as dictionary keys and every dictionary representing a row.
        """


def _safe_bool(boolstr:str) -> bool:

    if boolstr.upper()== "FALSE":
        return  False
    elif boolstr.upper()== "TRUE":
        return True
    else:
        raise Exception(f"Expected boolean string FALSE,TRUE in any casing, got '{boolstr}'.")


class AutoreportingDao(AutorepVariantDB):
    # group report columns read by get_group_report, using the current release's names
    GROUP_REPORT_COLUMNS: Final = frozenset([
        "chrom", "pos", "pval", "locus_id", "good_cs",
        "lead_enrichment", "lead_af_alt", "lead_most_severe_gene",
        "lead_mlogp", "lead_beta", "lead_sebeta",
        "functional_variants_strict", "credible_set_variants",
        "cs_size", "cs_log_bayes_factor",
        "specific_efo_trait_associations_strict", "specific_efo_trait_associations_relaxed",
        "found_associations_strict", "found_associations_relaxed",
    ])
    # columns that cannot be mapped to None (=cannot be omitted)
    REQUIRED_COLUMNS: Final = frozenset(["locus_id"])

    def __init__(self, authentication_file, group_report_path,
                 columns: Optional[Dict[str, Optional[str]]] = None):
        """
        :param columns: optional mapping from a group report column name to the name
                        used in this release's files, for releases whose columns differ
                        from the current ones. Map a column to None when it does not exist
                        in the release; it is then reported as NA. Columns in
                        REQUIRED_COLUMNS (locus_id) cannot be omitted. Columns that are not
                        listed are read using their current name.
        """
        self.authentication_file = authentication_file
        self.group_report_path = group_report_path
        self.columns = columns if columns is not None else {}
        unknown_columns = set(self.columns) - self.GROUP_REPORT_COLUMNS
        if unknown_columns:
            raise ValueError(f"Unknown autoreporting group report columns in config: {sorted(unknown_columns)}")
        omitted_required = [c for c in self.REQUIRED_COLUMNS if self.columns.get(c, c) is None]
        if omitted_required:
            raise ValueError(f"Autoreporting group report columns cannot be omitted: {omitted_required}")
        auth_module = load_source("mysql_auth", self.authentication_file)
        self.user = getattr(auth_module, "mysql")["user"]
        self.password = getattr(auth_module, "mysql")["password"]
        self.host = getattr(auth_module, "mysql")["host"]
        self.db = getattr(auth_module, "mysql")["db"]
        self.release = getattr(auth_module, "mysql")["release"]

    def get_connection(self):
        return pymysql.connect(
            host=self.host, user=self.user, password=self.password, db=self.db
        )

    def get_group_variants(self, phenotype, locus_id):
        try:
            conn = self.get_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cursori:
                sql = "SELECT * FROM autoreporting_variants WHERE rel=%s AND phenotype=%s AND locus_id=%s"
                cursori.execute(sql, ["r{}".format(self.release), phenotype, locus_id])
                result = cursori.fetchall()
            return result
        finally:
            conn.close()



    def get_group_report(self,phenotype) -> List[Dict[str,Union[str,int,float,bool]]]:
        """Returns the records in a group report as a list of dictionaries, one for each group.
        Dictionary keys, with value: value identifier (key):
        locus lead variant: locus_id
        phenotype name: phenocode
        cs quality: good_cs
        chromosome : chrom
        pvalue: pval
        lead mlogp: lead_mlogp
        lead beta: lead_beta
        lead Finnish enrichment: lead_enrichment
        lead alt allele af: lead_af_alt
        lead most severe gene: lead_most_severe_gene
        functional variants in cs: functional_variants_strict
        cs variants: credible_set_variants
        cs size: cs_size
        cs log10bf: cs_log_bayes_factor
        lead sebeta: lead_sebeta

        """

        filename = os.path.join(self.group_report_path,f"{phenotype}.top.out")
        if os.path.exists(filename):
            with open(filename) as f:
                hdr = f.readline().strip("\n").split("\t")
                hdi = {a:i for i,a in enumerate(hdr)}

                def has_col(name):
                    source = self.columns.get(name, name)
                    if name in self.columns and source is not None and source not in hdi:
                        raise ValueError(f"Configured column '{source}' for '{name}' not found in {filename}")
                    return source is not None and source in hdi

                def get_col(cols, name):
                    # read a column by its current name, translated via the configured
                    # column mapping; columns mapped to None are reported as NA
                    source = self.columns.get(name, name)
                    if source is None:
                        return "NA"
                    return cols[hdi[source]]

                def to_float(value):
                    return float(value) if value not in ("NA", "") else float("nan")

                def to_int(value):
                    return int(value) if value not in ("NA", "") else float("nan")
                
                #filter out empty and missing entries from traits
                merge_func = lambda a,b : ";".join(list(filter(lambda x:(x!="NA" and x != ""),[a,b])))

                data = []
                for _line in f:
                    cols = _line.strip("\n").split("\t")
                    good_cs = get_col(cols, "good_cs")
                    record = {
                        "chrom":get_col(cols, "chrom"),
                        "pval":to_float(get_col(cols, "pval")),
                        "lead_enrichment":to_float(get_col(cols, "lead_enrichment")),
                        "lead_af_alt":to_float(get_col(cols, "lead_af_alt")),
                        "lead_most_severe_gene":get_col(cols, "lead_most_severe_gene"),
                        "locus_id":get_col(cols, "locus_id"),
                        "phenocode":phenotype,
                        "good_cs":_safe_bool(good_cs) if good_cs != "NA" else "NA",
                        "lead_mlogp":to_float(get_col(cols, "lead_mlogp")),
                        "lead_beta":to_float(get_col(cols, "lead_beta")),
                        "functional_variants_strict":get_col(cols, "functional_variants_strict"),
                        "credible_set_variants":get_col(cols, "credible_set_variants"),
                        "cs_size":to_int(get_col(cols, "cs_size")),
                        "cs_log_bayes_factor":to_float(get_col(cols, "cs_log_bayes_factor")),
                        "lead_sebeta": get_col(cols, "lead_sebeta"),
                        "pos":get_col(cols, "pos"),
                    }
                    #compute lead mlogp from lead pval when it is not available, e.g. in older releases
                    if math.isnan(record["lead_mlogp"]) and not math.isnan(record["pval"]):
                        record["lead_mlogp"] = float(-math.log10(record["pval"])) if record["pval"] > 0 else float("inf")
                    
                    merge_func = lambda a,b : ";".join(list(filter(lambda x:(x!="NA" and x != ""),[a,b])))
                    #join trait cols
                    if has_col("specific_efo_trait_associations_strict"):
                        all_traits_strict = merge_func(
                            get_col(cols, "specific_efo_trait_associations_strict"),
                            get_col(cols, "found_associations_strict")
                        )
                        all_traits_strict = "NA" if all_traits_strict == "" else all_traits_strict
                    else:
                        all_traits_strict = get_col(cols, "found_associations_strict")
                    if has_col("specific_efo_trait_associations_relaxed"):
                        all_traits_relaxed = merge_func(
                            get_col(cols, "specific_efo_trait_associations_relaxed"),
                            get_col(cols, "found_associations_relaxed")
                        )
                        all_traits_relaxed = "NA" if all_traits_relaxed == "" else all_traits_relaxed
                    else:
                        all_traits_relaxed = get_col(cols, "found_associations_relaxed")
                    record["all_traits_strict"] = all_traits_strict
                    record["all_traits_relaxed"] = all_traits_relaxed
                    #fill in NA for missing values
                    for key in record:
                        if record[key] == "":
                            record[key] = "NA"

                    data.append(record)
            return data
        return []

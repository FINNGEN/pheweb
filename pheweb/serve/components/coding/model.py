# -*- coding: utf-8 -*-
"""
Coding data model classes.

DAO, DTO classes and interfaces.
"""
import abc
import typing
from collections import defaultdict as dd
from dataclasses import dataclass
import typing


def set_top_flags(results):
    # figure out top variant for each pheno
    # and top pheno for each variant
    pheno2top = dd(lambda: ('variant', 0))
    var2top = dd(lambda: ('pheno', 0))
    for res in results:
        code = res['pheno']['code']
        variant = res['variant']
        p_add = res['mlogp_add']
        p_chip = res['mlogp_chip']
        if p_add is not None and p_add > pheno2top[code][1]:
            pheno2top[code] = (variant, p_add)
        if p_chip is not None and p_chip > pheno2top[code][1]:
            pheno2top[code] = (variant, p_chip)
        if p_add is not None and p_add > var2top[variant][1]:
            var2top[variant] = (code, p_add)
        if p_chip is not None and p_chip > var2top[variant][1]:
            var2top[variant] = (code, p_chip)
    for res in results:
        if res['variant'] == pheno2top[res['pheno']['code']][0]:
            res['is_top_variant'] = True
        if res['pheno']['code'] == var2top[res['variant']][0]:
            res['is_top_pheno'] = True


class CodingDB(abc.ABC):
    """
    Coding DB.

    Abstract class for coding dao.
    """
    @abc.abstractmethod
    def get_top_results(self):
        pass

    @abc.abstractmethod
    def get_by_variant(self, query):
        pass
    
    @abc.abstractmethod
    def get_by_gene(self, query):
        pass

    @abc.abstractmethod
    def get_by_phenotype(self, phenocode):
        pass

    @abc.abstractmethod
    def get_autocomplete(self, query):
        """
        Suggest genes, variants and phenotypes matching a search query.

        Returns [{"type": "gene" | "variant" | "phenotype", "value": ..., "label": ...}]
        """
        pass

    @abc.abstractmethod
    def get_cluster_plot(self, variant):
        pass




@dataclass
class JeevesContext:
    """
    Jeeves context.

    Type interface for the jeeves context.
    """

    coding_dao: typing.Optional[CodingDB]

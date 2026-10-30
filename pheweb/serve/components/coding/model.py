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

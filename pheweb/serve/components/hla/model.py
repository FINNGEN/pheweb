# -*- coding: utf-8 -*-
"""
HLA Summary data model classes.

DAO, DTO classes and interfaces.
"""
import typing
from dataclasses import dataclass
import abc


class HLADB(abc.ABC):
    @abc.abstractmethod
    def get_top_results(self):
        """Retrieve top HLA results (mlogp > 5)
        """
        return

    @abc.abstractmethod
    def get_autocomplete(self):
        """Retrieve HLA autocomplete results
        """
        return

    @abc.abstractmethod
    def get_by_phenocode(self, phenocode):
        """Retrieve all HLA data for a phenocode
        """
        return
    
    @abc.abstractmethod
    def get_by_gene(self, gene):
        """Retrieve all HLA data for a gene
        """
        return

    @abc.abstractmethod
    def get_by_variant(self, variant):
        """Retrieve all HLA data for a variant
        """
        return

@dataclass
class JeevesContext:
    """
    Jeeves context.

    Type interface for the jeeves context.
    """

    hla_dao: typing.Optional[HLADB]
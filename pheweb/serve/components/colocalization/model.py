import abc
import attr
import typing
import attr
from attr.validators import instance_of
from sqlalchemy import Table, MetaData, create_engine, Column, Integer, String, Float, Text, ForeignKey
from pheweb.serve.components.colocalization.finngen_common_data_model.data import JSONifiable, Kwargs
from pheweb.serve.components.colocalization.finngen_common_data_model.genomics import Variant, Locus
import re

@attr.s
class CausalVariantVector(JSONifiable, Kwargs):
    """ Vector of causal variants
    """
    position = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(int)),
                                                               iterable_validator=instance_of(typing.List)))

    variant = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(str)),
                                                              iterable_validator=instance_of(typing.List)))

    pip1 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(float)),
                                                           iterable_validator=instance_of(typing.List)))

    pip2 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(float)),
                                                           iterable_validator=instance_of(typing.List)))

    beta1 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(float)),
                                                            iterable_validator=instance_of(typing.List)))

    beta2 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(float)),
                                                            iterable_validator=instance_of(typing.List)))

    causal_variant_id = attr.ib(validator=attr.validators.deep_iterable(member_validator=instance_of(int),
                                                                        iterable_validator=instance_of(typing.List)))

    count_cs = attr.ib(validator=attr.validators.deep_iterable(member_validator=instance_of(int),
                                                               iterable_validator=instance_of(typing.List)))

    phenotype1 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(str)),
                                                                 iterable_validator=instance_of(typing.List)))

    phenotype1_description = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(str)),
                                                                             iterable_validator=instance_of(typing.List)))

    phenotype2 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(str)),
                                                                 iterable_validator=instance_of(typing.List)))

    phenotype2_description = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(str)),
                                                                             iterable_validator=instance_of(typing.List)))


    def json_rep(self):
        return self.__dict__

    def __repr__(self) -> typing.Dict[str, typing.Any]:
        return self.__dict__


@attr.s
class VariantVector(JSONifiable, Kwargs):
    beta1 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(float)),
                                                            iterable_validator=instance_of(typing.List)))

    beta2 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(float)),
                                                            iterable_validator=instance_of(typing.List)))
    
    cs1 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(int)),
                                                          iterable_validator=instance_of(typing.List)))
    
    cs2 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(int)),
                                                          iterable_validator=instance_of(typing.List)))

    cs_specific_prob1 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(float)),
                                                                        iterable_validator=instance_of(typing.List)))
    
    cs_specific_prob2 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(float)),
                                                                        iterable_validator=instance_of(typing.List)))
    
    low_purity1 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(bool)),
                                                                  iterable_validator=instance_of(typing.List)))

    low_purity2 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(bool)),
                                                                  iterable_validator=instance_of(typing.List)))

    p1 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(float)),
                                                         iterable_validator=instance_of(typing.List)))

    p2 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(float)),
                                                         iterable_validator=instance_of(typing.List)))

    se1 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(float)),
                                                          iterable_validator=instance_of(typing.List)))
    
    se2 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(float)),
                                                          iterable_validator=instance_of(typing.List)))
    rsid = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(str)),
                                                           iterable_validator=instance_of(typing.List)))
    
    position = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(int)),
                                                               iterable_validator=instance_of(typing.List)))

    trait1 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(str)),
                                                             iterable_validator=instance_of(typing.List)))

    trait2 = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(instance_of(str)),
                                                             iterable_validator=instance_of(typing.List)))

    def json_rep(self):
        return { ** self.__dict__ , 'causal_variant_id' : self.rsid , 'variant' : self.rsid , 'pip1' : self.p1  , 'pip2' : self.p1 , 'count_cs' : self.cs1,
                 'phenotype1' : self.trait1 , 'phenotype2' : self.trait2,
                 'phenotype1_description' : self.trait1 ,  'phenotype2_description' : self.trait2  }

    def __repr__(self) -> typing.Dict[str, typing.Any]:
        return self.__dict__

    
@attr.s
class GenericArray(JSONifiable):
    values = attr.ib(validator=attr.validators.deep_iterable(member_validator=attr.validators.optional(attr.validators.instance_of(dict)),
                                                             iterable_validator=attr.validators.instance_of(typing.List)))


    def __repr__(self) -> typing.List[typing.Dict[str, typing.Any]]:
        return self.values

@attr.s
class GenericValue(JSONifiable):
    value = attr.ib(validator=attr.validators.optional(attr.validators.instance_of(dict)))
                    
    def json_rep(self):
        return self.value

    def __repr__(self) -> typing.Dict[str, typing.Any]:
        return self.value
    
    
@attr.s
class SearchSummary(JSONifiable):
    """
    DTO containing a summary of colocalization records for a search.

    count: number of records found
    unique_phenotype2: the number of unique phenotypes found
    unique_tissue2: the number of unique tissues found
    """
    count = attr.ib(validator=instance_of(int))
    unique_phenotype2 = attr.ib(validator=instance_of(int))
    unique_tissue2 = attr.ib(validator=instance_of(int))

    def json_rep(self) -> typing.Dict[str, typing.Any]:
        return self.__dict__


@attr.s
class SearchResults(JSONifiable):
    """
    DTO containing the results of a search.

    count: number of records matched, note this may be different
           from the size of colocalization if a limit term
           is used.
    colocalization: list of colocalization matches
    """
    count = attr.ib(validator=instance_of(int))
    colocalizations  = attr.ib()

    def json_rep(self):
        return {"count": self.count,
                "colocalizations": [c.json_rep() for c in self.colocalizations]}


@attr.s
class PhenotypeList(JSONifiable):
    """
    DTO containing a list of phenotypes.
    """
    phenotypes = attr.ib(validator=attr.validators.deep_iterable(member_validator=instance_of(str),
                                                                 iterable_validator=instance_of(typing.List)))

    def json_rep(self) -> typing.Dict[str, typing.Any]:
        return self.__dict__


class ColocalizationDB:


    @abc.abstractmethod
    def get_phenotype(self) -> PhenotypeList:
        """
        Return a list of phenotypes (phenotype1)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_locus(self,
                  phenotype: str,
                  locus: Locus,
                  flags: typing.Dict[str, typing.Any]) -> SearchResults:
        """
        Search for colocalization that match
        phenotype and range and return them.

        :param phenotype: phenotype to match in search
        :param chromosome_range: chromosome range to search
        :param flags: a collection of optional flags

        :return: matching colocalizations
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_locuszoom(self,
                        phenotype: str,
                        locus: Locus,
                        flags: typing.Dict[str, typing.Any]={}):
        raise NotImplementedError

    @abc.abstractmethod
    def get_variant(self,
                    phenotype: str,
                    variant: Variant,
                    flags: typing.Dict[str, typing.Any]) -> SearchResults:
        """
        Search for colocalization that match
        phenotype and range a summary of matches.

        :param phenotype: phenotype to match in search
        :param chromosome_range: chromosome range to search
        :param flags: a collection of optional flags

        :return: summary of matching colocalizations
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_locus_summary(self,
                          phenotype: str,
                          locus: Locus,
                          flags: typing.Dict[str, typing.Any] = {}) -> SearchSummary:
        raise NotImplementedError


    @abc.abstractmethod
    def get_colocalization(self,
                           colocalization_id : int,
                           flags : typing.Dict[str, typing.Any] = {}):
        """
        Given the identifier for a colocaliztion
        record return colocaliztion record.

        :param colocalization_id to search for
        :return: colocaliztion if one was found
        """
        raise NotImplementedError

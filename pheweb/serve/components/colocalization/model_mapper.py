import typing
from sqlalchemy import Table, MetaData, create_engine, Column, Integer, String, Float, Text, ForeignKey, Index
from sqlalchemy.orm import mapper, composite, relationship

from pheweb.serve.components.colocalization.finngen_common_data_model.genomics import Variant, Locus
from pheweb.serve.components.colocalization.finngen_common_data_model.colocalization import CausalVariant, Colocalization
from pheweb.serve.components.colocalization.model import CausalVariantVector, SearchSummary, SearchResults, PhenotypeList, ColocalizationDB

def NullableVariant(chromosome : typing.Optional[str],
                    position : typing.Optional[int],
                    reference : typing.Optional[str],
                    alternate : typing.Optional[str]) -> typing.Optional[Variant] :
    if chromosome and position and reference and alternate:
        return Variant(chromosome, position, reference, alternate)
    else:
        return None


class ColocalizationMapping():
    # see : https://gist.github.com/pazdera/1098129
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ColocalizationMapping.__instance == None:
            ColocalizationMapping()
        return ColocalizationMapping.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if ColocalizationMapping.__instance != None:
            raise Exception("singleton: use getInstance")
        else:
            ColocalizationMapping.__instance = self
            self.initialize()

    def getMetadata(self):
        return self.metadata

    def getTables(self):
        return [ self.causal_variant_table,
                 self.colocalization_table ]

    def getIndices(self):
        return [ self.colocalization_chromosome,
                 self.colocalization_start,
                 self.colocalization_stop,
                 self.colocalization_phenotype1,
                 self.colocalization_phenotype2,
                 self.colocalization_phenotype1_chromosome,
                 self.causal_variant_chromosome_position,
                 self.causal_variant_position_chromosome_colocalization_id ]

    def initialize(self):
        metadata = MetaData()
        self.metadata = metadata

        # Table
        colocalization_table = Table('colocalization',
                                     metadata,
                                     *Colocalization.columns())

        self.colocalization_table = colocalization_table

        self.colocalization_chromosome = Index('colocalization_chromosome',
                                               colocalization_table.c.chromosome)

        self.colocalization_start = Index('colocalization_start',
                                          colocalization_table.c.start)

        self.colocalization_stop = Index('colocalization_stop',
                                         colocalization_table.c.stop)

        self.colocalization_phenotype1 = Index('colocalization_phenotype1',
                                               colocalization_table.c.phenotype1)

        self.colocalization_phenotype2 = Index('colocalization_phenotype2',
                                               colocalization_table.c.phenotype2)

        self.colocalization_phenotype1_chromosome = Index('colocalization_phenotype1_chromosome',
                                                          colocalization_table.c.phenotype1,
                                                          colocalization_table.c.chromosome)

        causal_variant_table = Table('causal_variant',
                                     metadata,
                                     *CausalVariant.columns(),
                                     Column('colocalization_id', Integer, ForeignKey('colocalization.colocalization_id')))

        self.causal_variant_table = causal_variant_table

        self.causal_variant_chromosome_position = Index('causal_variant_position_chromosome',
                                                        causal_variant_table.c.variant_position,
                                                        causal_variant_table.c.variant_chromosome)

        self.causal_variant_position_chromosome_colocalization_id = Index('causal_variant_position_chromosome_colocalization_id',
                                                                          causal_variant_table.c.variant_position,
                                                                          causal_variant_table.c.variant_chromosome,
                                                                          causal_variant_table.c.colocalization_id)

        causal_variant_mapper = mapper(CausalVariant,
                                       causal_variant_table,
                                       properties = { 'variant': composite(NullableVariant,
                                                                           causal_variant_table.c.variant_chromosome,
                                                                           causal_variant_table.c.variant_position,
                                                                           causal_variant_table.c.variant_ref,
                                                                           causal_variant_table.c.variant_alt)
                                       })

        cluster_coordinate_mapper = mapper(Colocalization,
                                           colocalization_table,
                                           properties={'locus_id1': composite(Variant,
                                                                              colocalization_table.c.locus_id1_chromosome,
                                                                              colocalization_table.c.locus_id1_position,
                                                                              colocalization_table.c.locus_id1_ref,
                                                                              colocalization_table.c.locus_id1_alt),
                                                       'locus_id2': composite(Variant,
                                                                              colocalization_table.c.locus_id2_chromosome,
                                                                              colocalization_table.c.locus_id2_position,
                                                                              colocalization_table.c.locus_id2_ref,
                                                                              colocalization_table.c.locus_id2_alt),

                                                       'locus': composite(Locus,
                                                                          colocalization_table.c.chromosome,
                                                                          colocalization_table.c.start,
                                                                          colocalization_table.c.stop),

                                                       'variants': relationship(CausalVariant, lazy="joined"),
                                       })

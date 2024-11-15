import abc
import attr
import typing
import attr
from attr.validators import instance_of
from sqlalchemy import Table, MetaData, create_engine, Column, Integer, String, Float, Text
from pheweb.serve.components.colocalization.finngen_common_data_model.genomics import *
from pheweb.serve.components.colocalization.finngen_common_data_model.data import *


@attr.s
class CausalVariant(JSONifiable, Kwargs):
    """
    Causual variant DTO

    pip1, beta1
    pip2, beta2

    """
    rel = attr.ib(validator=instance_of(int))

    pip1 = attr.ib(validator=attr.validators.optional(instance_of(float)), default=None)
    beta1 = attr.ib(validator=attr.validators.optional(instance_of(float)), default=None)

    pip2 = attr.ib(validator=attr.validators.optional(instance_of(float)), default=None)
    beta2 = attr.ib(validator=attr.validators.optional(instance_of(float)), default=None)

    causal_variant_id = attr.ib(validator=attr.validators.optional(instance_of(int)), default=None)

    variant = attr.ib(instance_of(Variant))

    # id : note this is skipped as it is managed by SQL Alchemy

    @staticmethod
    def sort_key(c):
        """
        Compare method for sorting causal variants.
        The variants are sorted by the variant.

        :param c:
        :return: sort key
        """
        return Variant.sort_key(c.variant)

    def kwargs_rep(self) -> typing.Dict[str, typing.Any]:
        """
        Return the parameters to construct the
        causal variant.

        :return: kwargs
        """
        return {x: self.__dict__[x] for x in ["rel",
                                              "variant",
                                              "pip1",
                                              "beta1",
                                              "pip2",
                                              "beta2",
                                              "causal_variant_id"]}

    def json_rep(self):
        """
        Returns the json representation of the
        object.

        :return: json
        """
        d = {}
        d["rel"] = self.rel
        d["pip1"] = self.pip1
        d["beta1"] = self.beta1
        d["pip2"] = self.pip2
        d["beta2"] = self.beta2
        d["causal_variant_id"] = self.causal_variant_id
        d["position"] = self.variant.position if self.variant else None
        d["variant"] = str(self.variant) if self.variant else None
        d["count_cs"] = self.count_cs()
        d["membership_cs"] = self.membership_cs()
        return d

    def has_cs1(self) -> bool:
        """
        Returns if this causal variant has a first credible
        set.
        :return: boolean that is true if there is a first credible set
        """
        return (self.pip1 is not None) and (self.beta1 is not None)

    def has_cs2(self) -> bool:
        """
        Returns if this causal variant has a second credible
        set.
        :return: boolean that is true if there is a second credible set
        """
        return (self.pip2 is not None) and (self.beta2 is not None)

    def count_cs1(self) -> int:
        """
        Returns the number of first credible sets (0 or 1)
        set.
        :return: number of first credible sets (0 or 1)
        """
        return 1 if self.has_cs1() else 0

    def count_cs2(self) -> int:
        """
        Returns the number of second credible sets (0 or 1)
        set.
        :return: number of second credible sets (0 or 1)
        """
        return 1 if self.has_cs2() else 0

    def count_cs(self) -> int:
        """
        Returns the number of credible sets (0 - 2)
        set.
        :return: number of credible sets (0 - 2)
        """
        return self.count_cs1() + self.count_cs2()

    def membership_cs(self) -> str:
        """
        Returns a label indicating the cardinality
        of the credible sets.
        :return: 'Both' , 'CS1' , 'CS2', 'None'
        """
        if self.has_cs1() and self.has_cs2():
            label = 'Both'
        elif self.has_cs1():
            label = 'CS1'
        elif self.has_cs2():
            label = 'CS2'
        else:
            label = 'None'
        return label

    @staticmethod
    def parse_causal_variant(x: str):
        """
        Parses fields in a casual variant
        :param x: returns the parsed casual variant
        :return:
        """
        variant_str, pip_str , beta_str = x.split(",") # type: typing.Tuple[str, typing.Optional[str], typing.Optional[str]]
        pip : typing.Optional[float]
        if pip_str is None or pip_str == "" or pip_str == "NA":
            pip = None
        else:
            pip = float(pip_str)

        beta : typing.Optional[float]
        if beta_str is None or beta_str == "" or beta_str == "NA":
            beta = None
        else:
            beta = float(beta_str)

        return pip, beta

    @staticmethod
    def from_list(rel : str,
                  variant1_str: str,
                  variant2_str: str) -> typing.List["CausalVariant"]:
        """
        From two list of causal variants return
        the list of variants by combining their
        values to populate the pip's and the
        beta.

        :param variant1_str: variant 1
        :param variant2_str: variatn 2
        :return: list of causal variatns
        """
        vars1_index = {x.split(",")[0]: x for x in variant1_str.split(";")}
        vars2_index = {x.split(",")[0]: x for x in variant2_str.split(";")}

        split = CausalVariant.parse_causal_variant

        # list of all variants
        keys = {*vars1_index.keys(), *vars2_index.keys()}
        # lookup variants in the two indexes
        keys = map(lambda x: [x, vars1_index.get(x), vars2_index.get(x)], keys)

        keys = [[Variant.from_str(x[0]), nvl(x[1], split), nvl(x[2], split)] for x in keys]
        keys = [[rel,
                 *(k[1] or (None, None)),
                 *(k[2] or (None, None)),
                 None,
                 k[0]] for k in keys]

        causal_variants = [CausalVariant(*k) for k in keys]
        causal_variants = sorted(causal_variants, key=CausalVariant.sort_key)
        return causal_variants

    @staticmethod
    def columns(prefix: typing.Optional[str] = None) -> typing.List[Column]:
        """
        Return the sql alchemy definition of columns to
        hold a causal variant

        :param prefix: column prefix
        :return: sqlalchemy column definitions
        """
        prefix = prefix if prefix is not None else ""
        return [
            Column('{}rel'.format(prefix), SmallInteger, unique=False, nullable=False),
            Column('{}causal_variant_id'.format(prefix), Integer, primary_key=True, autoincrement=False),
            Column('{}pip1'.format(prefix), Float, unique=False, nullable=True),
            Column('{}pip2'.format(prefix), Float, unique=False, nullable=True),
            Column('{}beta1'.format(prefix), Float, unique=False, nullable=True),
            Column('{}beta2'.format(prefix), Float, unique=False, nullable=True),
            *Variant.columns('{}variant_'.format(prefix), nullable=False)
        ]

    @staticmethod
    def __composite_values__(self):
        """
        These are artifacts needed for composition by sqlalchemy.
        Returns a tuple containing the constructor args.

        :return: tuple (chromosome, start, stop)
        """
        return self.variant, self.pip1, self.pip2, self.beta1, self.beta2

    @staticmethod
    def db_column_names() -> typing.List[str]:
        return [c.name for c in CausalVariant.__attrs_attrs__]


@attr.s
class Colocalization(Kwargs, JSONifiable):
    """
    DTO for colocalization.


    https://github.com/FINNGEN/colocalization/blob/master/docs/data_dictionary.txt

    Note : the column order is defined here.  This column order determines
    how data is loaded.

    """
    rel = attr.ib(validator=instance_of(int))

    source1 = attr.ib(validator=instance_of(str))
    source2 = attr.ib(validator=instance_of(str))

    phenotype1 = attr.ib(validator=instance_of(str))
    phenotype1_description = attr.ib(validator=instance_of(str))

    phenotype2 = attr.ib(validator=instance_of(str))
    phenotype2_description = attr.ib(validator=instance_of(str))

    quant1 = attr.ib(validator=attr.validators.optional(instance_of(str)))
    quant2 = attr.ib(validator=attr.validators.optional(instance_of(str)))

    tissue1 = attr.ib(validator=attr.validators.optional(instance_of(str)))
    tissue2 = attr.ib(validator=attr.validators.optional(instance_of(str)))

    locus_id1 = attr.ib(validator=instance_of(Variant))
    locus_id2 = attr.ib(validator=instance_of(Variant))

    locus = attr.ib(validator=instance_of(Locus))

    len_cs1 = attr.ib(validator=instance_of(int))
    len_cs2 = attr.ib(validator=instance_of(int))
    len_inter = attr.ib(validator=instance_of(int))

    source2_displayname = attr.ib(validator=instance_of(str))
    pp_h4_abf = attr.ib(validator=instance_of(float))

    variants = attr.ib(validator=attr.validators.deep_iterable(member_validator=instance_of(CausalVariant),
                                                               iterable_validator=instance_of(typing.List)))

    colocalization_id = attr.ib(validator=attr.validators.optional(instance_of(int)), default=None)

    clpp = attr.ib(validator=attr.validators.optional(instance_of(float)), default=None)
    clpa = attr.ib(validator=attr.validators.optional(instance_of(float)), default=None)

    beta1 = attr.ib(validator=attr.validators.optional(instance_of(float)), default=None)
    beta2 = attr.ib(validator=attr.validators.optional(instance_of(float)), default=None)

    pval1 = attr.ib(validator=attr.validators.optional(instance_of(float)), default=None)
    pval2 = attr.ib(validator=attr.validators.optional(instance_of(float)), default=None)

    _IMPORT_COLUMN_NAMES = ('source1',
                            'source2',
                            'pheno1',
                            'pheno1_description',
                            'pheno2',
                            'pheno2_description',
                            'quant1',
                            'quant2',
                            'tissue1',
                            'tissue2',
                            'locus_id1',
                            'locus_id2',
                            'chrom',
                            'start',
                            'stop',
                            'clpp',
                            'clpa',
                            'vars',
                            'len_cs1',
                            'len_cs2',
                            'len_inter',
                            'vars1_info',
                            'vars2_info',
                            'source2_displayname',
                            'beta1',
                            'beta2',
                            'pval1',
                            'pval2',
                            'PP.H4.abf')

    @staticmethod
    def cvs_column_names() -> typing.List[str]:
        """
        List of csv column names

        :return:
        """
        return list(Colocalization._IMPORT_COLUMN_NAMES)

    def kwargs_rep(self) -> typing.Dict[str, typing.Any]:
        c = {name: getattr(self, name) for name in ["rel",
                                                    "source1", "source2",
                                                    "phenotype1", "phenotype1_description",
                                                    "phenotype2", "phenotype2_description",
                                                    "quant1", "quant2",
                                                    "tissue1", "tissue2",
                                                    "locus_id1", "locus_id2",
                                                    "locus",
                                                    "clpp", "clpa",
                                                    "len_cs1", "len_cs2", "len_inter",
                                                    "source2_displayname",
                                                    "beta1", "beta2", "pval1", "pval2", 'pp_h4_abf',
                                                    "colocalization_id"]}
        c["variants"] = list(map(lambda v: CausalVariant(**v.kwargs_rep()), self.variants))
        return c

    def json_rep(self):
        d = self.__dict__
        d["locus_id1"] = str(d["locus_id1"]) if self.locus_id1 else None
        d["locus_id2"] = str(d["locus_id2"]) if self.locus_id2 else None
        d["cs_size_1"] = sum(map(lambda c: c.count_cs1(), self.variants))
        d["cs_size_2"] = sum(map(lambda c: c.count_cs2(), self.variants))
        d["cs_size"] = 0 if self.variants is None else len(self.variants)
        d["variants"] = list(map(lambda c: c.json_rep(), self.variants))
        return d

    @staticmethod
    def db_column_names() -> typing.List[str]:
        return [c.name for c in Colocalization.__attrs_attrs__]

    @staticmethod
    def from_list(rel : str,
                  line: typing.List[str],
                  colocalization_id=None) -> "Colocalization":
        """
        Constructor method used to create colocalization from
        a row of data.

        the order of the columns are:
        01..05 source1, source2, phenotype1, phenotype1_description, phenotype2
        06..10 phenotype2_description, tissue1, tissue2, locus_id1, locus_id2
        11..15 chromosome, start, stop, clpp, clpa
        16..20 beta_id1, beta_id2, variation, vars_pip1, vars_pip2
        21..26 vars_beta1, vars_beta2, len_cs1, len_cs2, len_inter, source2_displayname
        27..31 beta1, beta2, pval1, pval2, pp_h4_abf

        :param colocalization_id: colocalization id
        :param line: string array with value
        :return: colocalization object
        """
        variants = CausalVariant.from_list(rel,
                                           nvl(line[21], str),
                                           nvl(line[22], str))

        colocalization = Colocalization(rel = rel,

                                        source1=nvl(line[0], str),
                                        source2=nvl(line[1], str),

                                        phenotype1=nvl(line[2], only_ascii),
                                        phenotype1_description=nvl(line[3], only_ascii),

                                        phenotype2=nvl(line[4], only_ascii),
                                        phenotype2_description=nvl(line[5], only_ascii),

                                        quant1=nvl(line[6], str),
                                        quant2=nvl(line[7], str),

                                        tissue1=nvl(line[8], str),
                                        tissue2=nvl(line[9], str),

                                        locus_id1=nvl(line[10], Variant.from_str),
                                        locus_id2=nvl(line[11], Variant.from_str),

                                        locus=Locus(nvl(line[12], string_to_chromosome),  # chromosome
                                                    nvl(line[13], na(int)),  # start
                                                    nvl(line[14], na(int))),  # stop

                                        clpp=nvl(line[15], float),
                                        clpa=nvl(line[16], float),
                                        # var line[17]
                                        len_cs1=nvl(line[18], na(int)),
                                        len_cs2=nvl(line[19], na(int)),
                                        len_inter=nvl(line[20], na(int)),

                                        source2_displayname=nvl(line[23], str),

                                        beta1=nvl(line[24], float),
                                        beta2=nvl(line[25], float),
                                        pval1=nvl(line[26], float),
                                        pval2=nvl(line[27], float),

                                        pp_h4_abf=nvl(line[28], float),

                                        variants=variants,

                                        colocalization_id=colocalization_id)
        return colocalization

    @staticmethod
    def from_str(rel : str, text: str, delimiter="\t") -> "Colocalization":
        line = text.split(delimiter)
        return Colocalization.from_list(rel, line)

    @staticmethod
    def columns(prefix: typing.Optional[str] = None) -> typing.List[Column]:
        prefix = prefix if prefix is not None else ""
        return [Column('{}rel'.format(prefix), SmallInteger, unique=False, nullable=False),

                Column('{}colocalization_id'.format(prefix), Integer, primary_key=True, autoincrement=False),
                Column('{}source1'.format(prefix), String(80), unique=False, nullable=False),
                Column('{}source2'.format(prefix), String(80), unique=False, nullable=False),
                Column('{}phenotype1'.format(prefix), String(500), unique=False, nullable=False),
                Column('{}phenotype1_description'.format(prefix), String(1000), unique=False, nullable=False),
                Column('{}phenotype2'.format(prefix), String(500), unique=False, nullable=False),
                Column('{}phenotype2_description'.format(prefix), String(1000), unique=False, nullable=False),

                Column('{}quant1'.format(prefix), String(80), unique=False, nullable=True),
                Column('{}quant2'.format(prefix), String(80), unique=False, nullable=True),

                Column('{}tissue1'.format(prefix), String(80), unique=False, nullable=True),
                Column('{}tissue2'.format(prefix), String(80), unique=False, nullable=True),

                # locus_id1
                *Variant.columns('{}locus_id1_'.format(prefix)),
                # locus_id2
                *Variant.columns('{}locus_id2_'.format(prefix)),

                # locus
                *Locus.columns(''),

                Column('{}clpp'.format(prefix), Float, unique=False, nullable=True),
                Column('{}clpa'.format(prefix), Float, unique=False, nullable=True),

                Column('{}len_cs1'.format(prefix), Integer, unique=False, nullable=False),
                Column('{}len_cs2'.format(prefix), Integer, unique=False, nullable=False),
                Column('{}len_inter'.format(prefix), Integer, unique=False, nullable=False),

                Column('{}source2_displayname'.format(prefix), String(1000), unique=False, nullable=True),

                Column('{}beta1'.format(prefix), Float, unique=False, nullable=True),
                Column('{}beta2'.format(prefix), Float, unique=False, nullable=True),
                Column('{}pval1'.format(prefix), Float, unique=False, nullable=True),
                Column('{}pval2'.format(prefix), Float, unique=False, nullable=True),

                Column('{}pp_h4_abf'.format(prefix), Float, unique=False, nullable=False),

                ]

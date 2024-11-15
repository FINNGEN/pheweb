import typing
import re
import typing

import attr
from attr.validators import instance_of
from sqlalchemy import Column, Integer, String, SmallInteger

from pheweb.serve.components.colocalization.finngen_common_data_model.data import JSONifiable, Kwargs

CHROMOSOME_MAP = {'X': 23, 'Y': 24, 'M': 25, 'MT': 25,
                  '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
                  '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                  '11': 11, '12': 12, '13': 13, '14': 14, '15': 15,
                  '16': 16, '17': 17, '18': 18, '19': 19, '20': 20,
                  '21': 21, '22': 22, '23': 23, '24': 24, '25': 25}


def string_to_chromosome(chromosome):
    return CHROMOSOME_MAP[chromosome]


# Variant
@attr.s(frozen=True)
class Variant(JSONifiable, Kwargs):
    """

    DTO containing variant information

    """
    chromosome = attr.ib(validator=instance_of(int))

    @chromosome.validator
    def chromosome_in_range(self, attribute, value):
        if not 1 <= value < 26:
            raise ValueError("value out of bounds")

    position = attr.ib(validator=instance_of(int))
    reference = attr.ib(validator=instance_of(str))
    alternate = attr.ib(validator=instance_of(str))

    PARSER = re.compile(r'''^(chr)?
                             (?P<chromosome>( M | MT | X | Y |
                                              1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
                                              11 | 12 | 13 | 14 | 15 |16 | 17 | 18 | 19 | 20 |
                                              21 | 22 | 23 | 24 | 25))

                             [_:/-]

                             (?P<position>\d+)

                             [_:/-]

                             (?P<reference>( \<[^\>]{1,998}\>
                                           | [ATGC]{1,1000} ))

                             [_:/-]

                             (?P<alternate>( \<[^\>]{1,998}\>
                                           | [ATGC]{1,1000} ))$
                        ''', re.VERBOSE)

    @staticmethod
    def normalize_str(text: str) -> str:
        return str(Variant.from_str(text))


    @staticmethod
    def from_str(text: str) -> typing.Optional["Variant"]:
        fragments = Variant.PARSER.match(text)
        if fragments is None:
            raise Exception(text)
        else:
            # @juhis
            # We'd like to represent chromosomes as integers,
            # X should be mapped to 23, Y to 24 and M or MT to 25.

            return Variant(chromosome=string_to_chromosome(fragments.group('chromosome')),
                           position=int(fragments.group('position')),
                           reference=fragments.group('reference'),
                           alternate=fragments.group('alternate'))

    def __str__(self) -> str:
        return "{chromosome}:{position}:{reference}:{alternate}".format(chromosome=self.chromosome,
                                                                        position=self.position,
                                                                        reference=self.reference,
                                                                        alternate=self.alternate)

    def json_rep(self):
        return self.__dict__

    def kwargs_rep(self) -> typing.Dict[str, typing.Any]:
        return self.__dict__

    @staticmethod
    def sort_key(v):
        return (v.chromosome,
                v.position,
                v.reference,
                v.alternate)

    @staticmethod
    def columns(prefix: typing.Optional[str] = None, primary_key=False, nullable=False) -> typing.List[Column]:
        prefix = prefix if prefix is not None else ""
        return [Column('{}chromosome'.format(prefix), SmallInteger, primary_key=primary_key, nullable=nullable),
                Column('{}position'.format(prefix), Integer, primary_key=primary_key, nullable=nullable),
                Column('{}ref'.format(prefix), String(1000), primary_key=primary_key, nullable=nullable),
                Column('{}alt'.format(prefix), String(1000), primary_key=primary_key, nullable=nullable), ]

    def __composite_values__(self):
        """
        These are artifacts needed for composition by sqlalchemy.
        Returns a tuple containing the constructor args.

        :return: tuple (chromosome, position, reference, alternate)
        """
        return self.chromosome, self.position, self.reference, self.alternate


#
@attr.s
class Locus(JSONifiable, Kwargs):
    """
        Chromosome coordinate range

        chromosome: chromosome
        start: start of range
        stop: end of range
    """
    chromosome = attr.ib(validator=attr.validators.and_(instance_of(int)))

    @chromosome.validator
    def chromosome_in_range(self, attribute, value):
        if not 1 <= value < 26:
            raise ValueError("value out of bounds")

    start = attr.ib(validator=instance_of(int))
    stop = attr.ib(validator=instance_of(int))

    PARSER = re.compile(r'''^(chr)?
                             (?P<chromosome>( M | MT | X | Y |
                                              1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
                                              11 | 12 | 13 | 14 | 15 |16 | 17 | 18 | 19 | 20 |
                                              21 | 22 | 23 | 24 | 25))

                             (?P<separator>[_:/])

                             (?P<start>\d+)

                             [_:/-]

                             (?P<stop>\d+)$
                        ''', re.VERBOSE)

    @staticmethod
    def from_str(text: str) -> typing.Optional["Locus"]:
        """
        Takes a string representing a range and returns a tuple of integers
        (chromosome,start,stop).  Returns None if it cannot be parsed.
        """

        fragments = Locus.PARSER.match(text)
        if fragments is None:
            raise Exception(text)
        else:
            start = int(fragments.group('start'))
            stop = int(fragments.group('stop'))
            if start > stop:
                raise Exception(text)
            else:
                return Locus(chromosome=string_to_chromosome(fragments.group('chromosome')),
                             start=start,
                             stop=stop)

    @staticmethod
    def sort_key(locus):
        return (locus.chromosome,
                locus.position,
                locus.start,
                locus.stop)

    def __str__(self):
        """

        :return: string representation of range
        """
        return "{chromosome}:{start}-{stop}".format(chromosome=self.chromosome,
                                                    start=self.start,
                                                    stop=self.stop)

    def json_rep(self):
        return self.__dict__

    def kwargs_rep(self) -> typing.Dict[str, typing.Any]:
        return self.__dict__

    @staticmethod
    def columns(prefix: typing.Optional[str] = None) -> typing.List[Column]:
        prefix = prefix if prefix is not None else ""
        return [Column('{}chromosome'.format(prefix), SmallInteger, unique=False, nullable=False),
                Column('{}start'.format(prefix), Integer, unique=False, nullable=False),
                Column('{}stop'.format(prefix), Integer, unique=False, nullable=False)]

    def __composite_values__(self):
        """
        These are artifacts needed for composition by sqlalchemy.
        Returns a tuple containing the constructor args.

        :return: tuple (chromosome, start, stop)
        """
        return self.chromosome, self.start, self.stop

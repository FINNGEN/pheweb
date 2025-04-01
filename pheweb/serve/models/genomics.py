import typing
import re
import typing

import attr
from attr.validators import instance_of

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
class Variant():
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

@attr.s
class Region():
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
    def from_str(text: str) -> typing.Optional["Region"]:
        """
        Takes a string representing a range and returns a tuple of integers
        (chromosome,start,stop).  Returns None if it cannot be parsed.
        """

        fragments = Region.PARSER.match(text)
        if fragments is None:
            raise Exception(text)
        else:
            start = int(fragments.group('start'))
            stop = int(fragments.group('stop'))
            if start > stop:
                raise Exception(text)
            else:
                return Region(chromosome=string_to_chromosome(fragments.group('chromosome')),
                             start=start,
                             stop=stop)

    def __str__(self):
        """

        :return: string representation of range
        """
        return "{chromosome}:{start}-{stop}".format(chromosome=self.chromosome,
                                                    start=self.start,
                                                    stop=self.stop)


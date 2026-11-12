# -*- coding: utf-8 -*-
import abc
import re

# chr-pos-ref-alt, separated by any of - _ : | /
VARIANT_RE = re.compile(r'^(?:chr)?0?([0-9]{1,2}|X|Y|MT?)[-_:|/]([0-9]+)[-_:|/]([ACGT]+)[-_:|/]([ACGT]+)$',
                        re.IGNORECASE)
CHROMOSOMES = {'X': 23, 'Y': 24, 'M': 25, 'MT': 25}


class JSONifiable(abc.ABC):
    @abc.abstractmethod
    def json_rep(self):
        """
        Return an object that can be jsonencoded.
        """


class Variant(JSONifiable):
    def __init__(self, chr, pos, ref, alt):
        try:
            self.chr = int(chr)
        except:
            raise Exception("Chromosome can be only numeric! Use x=23, y=24 and MT=25")

        self.pos = int(pos)
        self.ref = ref
        self.alt = alt
        self.varid = "{}:{}:{}:{}".format(self.chr, self.pos, self.ref, self.alt)
        self.annotation = {}

    @classmethod
    def from_str(cls, text: str) -> "Variant":
        """
        Parse a variant like 1-123-A-T, chrX:123:A:T or 23_123_a_t.
        Raises ValueError if the text is not a valid variant.
        """
        match = VARIANT_RE.match(text.strip())
        if match is None:
            raise ValueError('malformed variant {}, use chr-pos-ref-alt'.format(text))
        chrom, pos, ref, alt = match.groups()
        chrom = CHROMOSOMES.get(chrom.upper()) or int(chrom)
        if not 1 <= chrom <= 25:
            raise ValueError('supported chromosomes: 1-25, X, Y, M, MT')
        return cls(chrom, pos, ref.upper(), alt.upper())

    def add_annotation(self, name, value):
        self.annotation[name] = value

    @property
    def id(self):
        return self.varid

    @property
    def rsids(self):
        if "rsids" in self.annotation:
            return self.annotation["rsids"]
        else:
            return None

    @rsids.setter
    def rsids(self, value):
        self.annotation["rsids"] = value

    def get_annotation(self, name):
        if name in self.annotation:
            return self.annotation[name]
        else:
            return None

    def get_annotations(self):
        return self.annotation

    def merge_annot(self, other, overwrite=True):
        """
        Merges annotations from another Variant object. overwrite determines if annotation with the same name is overwritten or kept
        """
        for k, v in other.get_annotations():
            if k not in self.annotation or overwrite:
                self.add_annotation(k, v)

    def __eq__(self, other):
        return (
            self.chr == other.chr
            and self.pos == other.pos
            and self.ref == other.ref
            and self.alt == other.alt
        )

    def __hash__(self):
        return hash(self.varid)

    def __repr__(self):
        return self.varid

    def json_rep(self):
        return self.__dict__

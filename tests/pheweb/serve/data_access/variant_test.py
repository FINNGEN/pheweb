# -*- coding: utf-8 -*-
"""
Variant test.
"""
import pytest

from pheweb.serve.data_access.variant import Variant


@pytest.mark.unit
@pytest.mark.parametrize("text, expected", [
    ("1-925969-C-T", (1, 925969, "C", "T")),
    ("chrX:284258:t:c", (23, 284258, "T", "C")),
    ("23_284258_T_C", (23, 284258, "T", "C")),
    ("01|1|A|G", (1, 1, "A", "G")),
    ("MT/1/A/G", (25, 1, "A", "G")),
    ("m-1-A-G", (25, 1, "A", "G")),
    ("Y-5-A-G", (24, 5, "A", "G")),
    ("CHR22-5-AC-G", (22, 5, "AC", "G")),
    (" 1-2-A-T ", (1, 2, "A", "T")),
])
def test_from_str(text, expected) -> None:
    variant = Variant.from_str(text)
    assert (variant.chr, variant.pos, variant.ref, variant.alt) == expected


@pytest.mark.unit
@pytest.mark.parametrize("text", [
    "", "foo", "chr", "1-2-A", "1-2-A-T-G", "1-x-A-T", "1-2-N-T", "1-2-A-",
    "0-1-A-T", "26-1-A-T", "1-2-A-T-",
])
def test_from_str_malformed(text) -> None:
    with pytest.raises(ValueError):
        Variant.from_str(text)


@pytest.mark.unit
def test_from_str_equals_constructor() -> None:
    assert Variant.from_str("X-1-A-T") == Variant(23, 1, "A", "T")
    assert str(Variant.from_str("X-1-A-T")) == "23:1:A:T"

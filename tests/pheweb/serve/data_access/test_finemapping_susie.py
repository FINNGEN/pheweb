# -*- coding: utf-8 -*-

"""
Unit test for finemapping susie module.

See: pheweb/serve/data_access/finemapping_susie.py

"""


import uuid
from unittest.mock import patch
from pathlib import Path
import json

import pytest

from pheweb.serve.data_access.finemapping_susie import (
    format_rsid,
    parse_susie_summary
)


@pytest.mark.unit
def test_format_rsid() -> None:
    """
    Test nvl formatting rsid.

    @return: None
    """
    row = { "chr" : 1 , "position" : 2 , "ref" : "A" , "alt" : "C" }
    assert format_rsid(row) == "chr1_2_A_C"

@pytest.mark.unit
def test_parse_susie_summary_missing_file() -> None:
    """
    Test missing summary file return
    an empty map
    """
    assert parse_susie_summary("", "region") == {}


@pytest.mark.unit
def test_parse_susie_summary_sample_file() -> None:
    """
    Test missing summary file return
    an empty map
    """
    sample_file = Path(__file__).resolve().parent / "data/TEST.SUSIE.cred.summary.tsv"
    expected = Path(__file__).resolve().parent / "data/TEST.expected.1.json"

    with open(expected, 'r') as f:
        assert parse_susie_summary(sample_file, "chr7:25352046-28352046") == json.load(f)



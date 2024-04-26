# -*- coding: utf-8 -*-
import pytest
from pheweb.text_utils import text_to_boolean


from pheweb.command_line import run

@pytest.mark.unit
def test_format_summary_file() -> None:
    """
    Test format summary file.

    @return: None
    """
    assert text_to_boolean("") is None
    assert text_to_boolean("0") == False
    assert text_to_boolean("1") == True
    assert text_to_boolean("2") == None

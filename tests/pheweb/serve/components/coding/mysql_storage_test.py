# -*- coding: utf-8 -*-
"""
Coding MySQL DAO test.

The database connection is mocked, so these tests check the parameters
passed to the queries and the formatting of the returned rows.
"""
from unittest.mock import MagicMock

import pytest

# mysql_storage is imported by db.py, so load db.py first to avoid a circular import
import pheweb.serve.data_access.db  # noqa: F401
from pheweb.serve.components.coding.mysql_storage import (
    AUTOCOMPLETE_LIMIT,
    GENE_AUTOCOMPLETE_SQL,
    GENE_RESULTS_SQL,
    PHENOTYPE_AUTOCOMPLETE_SQL,
    PHENOTYPE_RESULTS_SQL,
    TOP_RESULTS_SQL,
    VARIANT_AUTOCOMPLETE_SQL,
    VARIANT_RESULTS_SQL,
    CodingMysqlDAO,
    escape_like,
    format_row,
    variant_prefix,
)
from pheweb.serve.data_access.variant import Variant


def make_row(**kwargs) -> dict:
    row = {
        "phenocode": "AB1_CANDIDIASIS",
        "phenostring": "Candidiasis",
        "variant": "1-925969-C-T",
        "af": 0.01,
        "info": 0.99,
        "rsid": "rs1",
        "most_severe": "missense_variant",
        "gene_most_severe": "SAMD11",
        "enrichment": 1.5,
        "mlogp_add": 2.0,
        "beta_add": 0.1,
        "sebeta_add": 0.01,
        "mlogp_chip_add": None,
        "beta_chip_add": None,
        "sebeta_chip_add": None,
        "mlogp_chip_rec": 5.0,
        "beta_chip_rec": 0.2,
        "sebeta_chip_rec": 0.02,
        "is_top_pheno": 1,
    }
    row.update(kwargs)
    return row


@pytest.fixture(name="cursor")
def fixture_cursor() -> MagicMock:
    """
    Cursor returned by the mocked connection.

    Set cursor.fetchall.side_effect to the rows each query returns.
    """
    return MagicMock()


@pytest.fixture(name="dao")
def fixture_dao(tmp_path, cursor) -> CodingMysqlDAO:
    """
    Create a DAO whose connection returns the mocked cursor.
    """
    auth = tmp_path / "mysql_auth.py"
    auth.write_text("mysql = {'host': 'localhost', 'user': 'user', 'password': 'password', 'db': 'db'}\n")
    dao = CodingMysqlDAO(str(auth), plot_root=str(tmp_path) + "/")
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    dao.get_connection = MagicMock(return_value=connection)
    return dao


def executed(cursor: MagicMock) -> list:
    """Return the (sql, params) of each query run on the cursor."""
    return [c.args for c in cursor.execute.call_args_list]


@pytest.mark.unit
def test_escape_like() -> None:
    assert escape_like("BRCA2") == "BRCA2"
    assert escape_like("50%") == "50\\%"
    assert escape_like("a_b") == "a\\_b"
    assert escape_like("a\\b") == "a\\\\b"


@pytest.mark.unit
@pytest.mark.parametrize("query, expected", [
    ("1", "1"),
    ("1-9259", "1:9259"),
    ("1-925969-c-t", "1:925969:C:T"),
    ("chrX_284", "23:284"),
    ("x:284258:t", "23:284258:T"),
    ("01-1", "1:1"),
    ("MT", "25"),
    ("m|1", "25:1"),
    ("23-1", "23:1"),
    (" 1-1 ", "1:1"),
])
def test_variant_prefix(query, expected) -> None:
    assert variant_prefix(query) == expected


@pytest.mark.unit
@pytest.mark.parametrize("query", ["BRCA2", "chr", "0", "26-1", "Candidiasis"])
def test_variant_prefix_not_variant(query) -> None:
    assert variant_prefix(query) is None


@pytest.mark.unit
def test_format_row() -> None:
    row = make_row()
    result = format_row(row)
    assert result["rec_add"] == 3.0
    assert result["possible_explaining_signals"] is None
    assert result["is_top_pheno"] is True
    assert result["enrichment"] == 1.5
    # the input row is not modified
    assert "rec_add" not in row


@pytest.mark.unit
def test_format_row_missing_values() -> None:
    assert format_row(make_row(mlogp_chip_rec=None))["rec_add"] is None
    assert format_row(make_row(mlogp_add=None))["rec_add"] is None
    assert format_row(make_row(enrichment=None))["enrichment"] is None
    assert format_row(make_row(is_top_pheno=0))["is_top_pheno"] is False


@pytest.mark.unit
def test_format_row_inf_enrichment() -> None:
    assert format_row(make_row(enrichment=1e300))["enrichment"] == "inf"


@pytest.mark.unit
def test_get_top_results(dao, cursor) -> None:
    cursor.fetchall.side_effect = [[make_row()]]
    result = dao.get_top_results()
    assert [r["phenocode"] for r in result["results"]] == ["AB1_CANDIDIASIS"]
    ((sql, params),) = executed(cursor)
    assert sql == TOP_RESULTS_SQL
    assert params == pytest.approx((5.0,))


@pytest.mark.unit
def test_get_top_results_cached(dao, cursor) -> None:
    cursor.fetchall.side_effect = [[make_row()]]
    assert dao.get_top_results() == dao.get_top_results()
    assert dao.get_connection.call_count == 1


@pytest.mark.unit
def test_get_by_variant(dao, cursor) -> None:
    cursor.fetchall.side_effect = [[make_row(variant="X-284258-T-C")]]
    result = dao.get_by_variant(Variant.from_str("X-284258-T-C"))
    assert result["results"][0]["variant"] == "X-284258-T-C"
    assert executed(cursor) == [(VARIANT_RESULTS_SQL, (23, 284258, "T", "C"))]


@pytest.mark.unit
def test_get_by_variant_no_results(dao, cursor) -> None:
    cursor.fetchall.side_effect = [[]]
    assert dao.get_by_variant(Variant.from_str("1-1-A-T")) == {"results": []}


@pytest.mark.unit
def test_get_by_gene(dao, cursor) -> None:
    cursor.fetchall.side_effect = [[make_row()]]
    assert len(dao.get_by_gene("SAMD11")["results"]) == 1
    # without a gene threshold every result is returned
    assert executed(cursor) == [(GENE_RESULTS_SQL, ("SAMD11", -1))]


@pytest.mark.unit
def test_get_by_gene_threshold(dao, cursor) -> None:
    cursor.fetchall.side_effect = [[]]
    dao.gene_threshold = 1e-4
    dao.get_by_gene("SAMD11")
    ((sql, (gene, min_mlogp)),) = executed(cursor)
    assert sql == GENE_RESULTS_SQL
    assert gene == "SAMD11"
    assert min_mlogp == pytest.approx(4.0)


@pytest.mark.unit
def test_get_by_phenotype(dao, cursor) -> None:
    cursor.fetchall.side_effect = [[make_row()]]
    assert len(dao.get_by_phenotype("AB1_CANDIDIASIS")["results"]) == 1
    assert executed(cursor) == [(PHENOTYPE_RESULTS_SQL, ("AB1_CANDIDIASIS",))]


@pytest.mark.unit
@pytest.mark.parametrize("query", ["", "   "])
def test_get_autocomplete_empty(dao, query) -> None:
    assert dao.get_autocomplete(query) == []
    dao.get_connection.assert_not_called()


@pytest.mark.unit
def test_get_autocomplete(dao, cursor) -> None:
    cursor.fetchall.side_effect = [
        [{"gene": "CAND1"}],
        [{"code": "AB1_CANDIDIASIS", "name": "Candidiasis"}],
    ]
    assert dao.get_autocomplete(" cand ") == [
        {"type": "gene", "value": "CAND1", "label": "CAND1"},
        {"type": "phenotype", "value": "AB1_CANDIDIASIS", "label": "Candidiasis (AB1_CANDIDIASIS)"},
    ]
    # not a variant, so variants are not searched
    assert executed(cursor) == [
        (GENE_AUTOCOMPLETE_SQL, ("cand%", AUTOCOMPLETE_LIMIT)),
        (PHENOTYPE_AUTOCOMPLETE_SQL, ("cand%", "%cand%", AUTOCOMPLETE_LIMIT)),
    ]


@pytest.mark.unit
def test_get_autocomplete_variant(dao, cursor) -> None:
    cursor.fetchall.side_effect = [
        [],
        [{"variant": "X-284258-T-C"}, {"variant": "X-284272-C-T"}],
        [],
    ]
    assert dao.get_autocomplete("chrX_2842") == [
        {"type": "variant", "value": "X-284258-T-C", "label": "X-284258-T-C"},
        {"type": "variant", "value": "X-284272-C-T", "label": "X-284272-C-T"},
    ]
    assert executed(cursor)[1] == (VARIANT_AUTOCOMPLETE_SQL, ("23:2842%", AUTOCOMPLETE_LIMIT))


@pytest.mark.unit
def test_get_autocomplete_escapes_wildcards(dao, cursor) -> None:
    cursor.fetchall.side_effect = [[], []]
    dao.get_autocomplete("a_b%")
    assert executed(cursor) == [
        (GENE_AUTOCOMPLETE_SQL, ("a\\_b\\%%", AUTOCOMPLETE_LIMIT)),
        (PHENOTYPE_AUTOCOMPLETE_SQL, ("a\\_b\\%%", "%a\\_b\\%%", AUTOCOMPLETE_LIMIT)),
    ]


@pytest.mark.unit
def test_get_cluster_plot(dao, tmp_path) -> None:
    (tmp_path / "X_284258_T_C.raw.png").write_bytes(b"png")
    (tmp_path / "1_925969_C_T.raw.png").write_bytes(b"png1")
    assert dao.get_cluster_plot("23:284258:T:C") == b"png"
    assert dao.get_cluster_plot("1:925969:C:T") == b"png1"


@pytest.mark.unit
def test_get_cluster_plot_missing(dao) -> None:
    assert dao.get_cluster_plot("1:1:A:T") is None

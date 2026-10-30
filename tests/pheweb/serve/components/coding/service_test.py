# -*- coding: utf-8 -*-
"""
Coding service test.
"""
import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.exceptions import NotFound

from pheweb.serve.components.coding.model import CodingDB, JeevesContext
from pheweb.serve.components.coding.service import coding, development, get_dao

ROW = {"phenocode": "AB1_CANDIDIASIS", "variant": "1-925969-C-T"}


class FakeCodingDAO(CodingDB):
    """
    Returns one row for SAMD11, AB1_CANDIDIASIS and 1-925969-C-T,
    and no results otherwise.
    """

    def get_top_results(self):
        return {"results": [ROW]}

    def get_by_variant(self, variant):
        found = (variant.chr, variant.pos, variant.ref, variant.alt) == (1, 925969, "C", "T")
        return {"results": [ROW] if found else []}

    def get_by_gene(self, gene):
        return {"results": [ROW] if gene == "SAMD11" else []}

    def get_by_phenotype(self, phenocode):
        return {"results": [ROW] if phenocode == "AB1_CANDIDIASIS" else []}

    def get_autocomplete(self, query):
        return [{"type": "gene", "value": query, "label": query}]

    def get_cluster_plot(self, variant):
        return b"png" if variant == "1:925969:C:T" else None


def make_client(dao) -> FlaskClient:
    app = Flask(__name__, instance_relative_config=True)
    app.register_blueprint(coding)
    app.register_blueprint(development)
    app.jeeves = JeevesContext(coding_dao=dao)
    return app.test_client()


@pytest.fixture(name="client")
def fixture_client() -> FlaskClient:
    with make_client(FakeCodingDAO()) as client:
        yield client


@pytest.fixture(name="bad_client")
def fixture_bad_client() -> FlaskClient:
    with make_client(None) as client:
        yield client


@pytest.mark.unit
def test_get_dao() -> None:
    dao = FakeCodingDAO()
    app = Flask(__name__, instance_relative_config=True)
    app.jeeves = JeevesContext(coding_dao=dao)
    assert get_dao(current_app=app) == dao


@pytest.mark.unit
def test_get_dao_missing() -> None:
    app = Flask(__name__, instance_relative_config=True)
    app.jeeves = JeevesContext(coding_dao=None)
    with pytest.raises(NotFound):
        get_dao(current_app=app)


@pytest.mark.unit
def test_dao_missing(bad_client) -> None:
    assert bad_client.get("/api/v1/coding/top").status_code == 404


@pytest.mark.unit
def test_top(client) -> None:
    response = client.get("/api/v1/coding/top")
    assert response.status_code == 200
    assert response.get_json() == {"results": [ROW]}


@pytest.mark.unit
@pytest.mark.parametrize("variant", ["1-925969-C-T", "chr1:925969:c:t", "1_925969_C_T"])
def test_variant(client, variant) -> None:
    response = client.get("/api/v1/coding/variant/" + variant)
    assert response.status_code == 200
    assert response.get_json() == {"results": [ROW]}


@pytest.mark.unit
def test_variant_no_results(client) -> None:
    response = client.get("/api/v1/coding/variant/2-1-A-T")
    assert response.status_code == 200
    assert response.get_json() == {"results": []}


@pytest.mark.unit
@pytest.mark.parametrize("variant", ["BRCA2", "1-925969-C", "26-1-A-T", "1-1-N-T"])
def test_variant_malformed(client, variant) -> None:
    response = client.get("/api/v1/coding/variant/" + variant)
    assert response.status_code == 400
    assert "message" in response.get_json()


@pytest.mark.unit
def test_gene(client) -> None:
    response = client.get("/api/v1/coding/gene/SAMD11")
    assert response.status_code == 200
    assert response.get_json() == {"results": [ROW]}


@pytest.mark.unit
def test_gene_no_results(client) -> None:
    response = client.get("/api/v1/coding/gene/NOSUCH")
    assert response.status_code == 200
    assert response.get_json() == {"results": []}


@pytest.mark.unit
def test_phenocode(client) -> None:
    response = client.get("/api/v1/coding/phenocode/AB1_CANDIDIASIS")
    assert response.status_code == 200
    assert response.get_json() == {"results": [ROW]}


@pytest.mark.unit
def test_phenocode_no_results(client) -> None:
    response = client.get("/api/v1/coding/phenocode/NOSUCH")
    assert response.status_code == 200
    assert response.get_json() == {"results": []}


@pytest.mark.unit
def test_autocomplete(client) -> None:
    response = client.get("/api/v1/coding/autocomplete?query=BRCA")
    assert response.status_code == 200
    assert response.get_json() == [{"type": "gene", "value": "BRCA", "label": "BRCA"}]


@pytest.mark.unit
def test_autocomplete_no_query(client) -> None:
    response = client.get("/api/v1/coding/autocomplete")
    assert response.status_code == 200
    assert response.get_json() == [{"type": "gene", "value": "", "label": ""}]


@pytest.mark.unit
def test_cluster_plot(client) -> None:
    response = client.get("/api/v1/coding/cluster_plot/1:925969:C:T")
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.data == b"png"


@pytest.mark.unit
def test_cluster_plot_missing(client) -> None:
    assert client.get("/api/v1/coding/cluster_plot/1:1:A:T").status_code == 404

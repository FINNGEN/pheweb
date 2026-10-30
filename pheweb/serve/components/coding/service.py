# -*- coding: utf-8 -*-
"""
Endpoint for coding data.

Methods for flask blueprints.
"""
import typing

from flask import (
    Blueprint,
    jsonify,
    current_app as app,
    abort,
    Response,
    request,
)

from .model import CodingDB, JeevesContext
from pheweb.serve.data_access.variant import Variant

coding = Blueprint("pheweb_coding", __name__)
development = Blueprint("development", __name__)


app.jeeves: JeevesContext  # type: ignore


def get_dao(current_app=app) -> CodingDB:
    """ "
    Get DAO.

    Get DAO object stored in jeeves.
    Return 404 if not available as
    it means the coding data is not
    available.
    """
    dao: typing.Optional[CodingDB] = current_app.jeeves.coding_dao
    if dao is None:
        result = None
        abort(404, "Coding data not available")
    else:
        result = dao
    return result


@coding.route('/api/v1/coding/top')
def top_data():
    return get_dao().get_top_results()

@coding.route('/api/v1/coding/variant/<variant>')
def get_by_variant(variant):
    try:
        var = Variant.from_str(variant)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(get_dao().get_by_variant(var))

@coding.route('/api/v1/coding/phenocode/<phenocode>')
def get_by_phenotype(phenocode):
    return jsonify(get_dao().get_by_phenotype(phenocode))

@coding.route('/api/v1/coding/autocomplete')
def get_autocomplete():
    return jsonify(get_dao().get_autocomplete(request.args.get('query', '')))

@coding.route('/api/v1/coding/gene/<gene>')
def get_by_gene(gene):
    return jsonify(get_dao().get_by_gene(gene))


@coding.route('/api/v1/coding/cluster_plot/<variant>', methods=["GET"])
def get_cluster_plot(variant : str):
    """
    Endpoint to return cluster plot for variant.

    :param variant: variant
    :return: response
    """
    dao: CodingDB = get_dao()
    data = dao.get_cluster_plot(variant)
    if data is None:
        result = None
        abort(404, "Requested cluster plot not found!")
    else:
        result = Response(data, mimetype="image/png")
    return result

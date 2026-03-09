# -*- coding: utf-8 -*-
"""
Endpoint for HLA Summary data.

Methods for flask blueprints.
"""
import typing

from flask import (
    Blueprint,
    jsonify,
    current_app as app,
    abort,
    Response,
)

from .model import HLADAO, JeevesContext

hla = Blueprint("pheweb_hla", __name__)
development = Blueprint("development", __name__)


app.jeeves: JeevesContext  # type: ignore


def get_dao(current_app=app) -> HLADAO:
    """ "
    Get DAO.

    Get DAO object stored in jeeves.
    Return 404 if not available as
    it means the HLA Summary data is not
    available.
    """
    dao: typing.Optional[HLADAO] = current_app.jeeves.hla_dao
    if dao is None:
        result = None
        abort(404, "HLA data not available")
    else:
        result = dao
    return result


@hla.route('/api/v1/hla/top')
def top_data():
    return get_dao().get_top_results()

@hla.route('/api/v1/hla/phenocode/<phenocode>')
def get_by_phenocode(phenocode):
    return get_dao().get_by_phenocode(phenocode)

@hla.route('/api/v1/hla/autocomplete')
def get_autocomplete():
    return get_dao().get_autocomplete()

@hla.route('/api/v1/hla/gene/<gene>')
def get_by_gene(gene):
    return get_dao().get_by_gene(gene)

@hla.route('/api/v1/hla/variant/<variant>')
def get_by_alt(variant):
    return get_dao().get_by_variant(variant)
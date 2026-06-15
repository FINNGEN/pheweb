# -*- coding: utf-8 -*-
"""
Endpoint for HLA Summary data.

Methods for flask blueprints.
"""
import typing

from flask import (
    Blueprint,
    current_app as app,
    abort,
    request,
)

from pheweb.serve.data_access.db import HLADB

from .model import JeevesContext

hla = Blueprint("pheweb_hla", __name__)
development = Blueprint("development", __name__)


app.jeeves: JeevesContext  # type: ignore


_MAX_LIMIT = 1000


def _parse_pagination(default_limit: int = 100):
    """Parse and validate ?page= and ?limit= query parameters."""
    try:
        limit = int(request.args.get("limit", default_limit))
        page = int(request.args.get("page", 1))
    except ValueError:
        abort(400, "page and limit must be integers")
    if limit < 1 or limit > _MAX_LIMIT:
        abort(400, f"limit must be between 1 and {_MAX_LIMIT}")
    if page < 1:
        abort(400, "page must be >= 1")
    return limit, page


def get_dao(current_app=app) -> HLADB:
    """ "
    Get DAO.

    Get DAO object stored in jeeves.
    Return 404 if not available as
    it means the HLA Summary data is not
    available.
    """
    dao: typing.Optional[HLADB] = current_app.jeeves.hla_dao
    if dao is None:
        result = None
        abort(404, "HLA data not available")
    else:
        result = dao
    return result


@hla.route('/api/v1/hla/top')
def top_data():
    limit, page = _parse_pagination()
    return get_dao().get_top_results(limit=limit, page=page)

@hla.route('/api/v1/hla/phenocode/<phenocode>')
def get_by_phenocode(phenocode):
    limit, page = _parse_pagination()
    return get_dao().get_by_phenocode(phenocode, limit=limit, page=page)

@hla.route('/api/v1/hla/autocomplete')
def get_autocomplete():
    return get_dao().get_autocomplete()

@hla.route('/api/v1/hla/gene/<gene>')
def get_by_gene(gene):
    limit, page = _parse_pagination()
    return get_dao().get_by_gene(gene, limit=limit, page=page)

@hla.route('/api/v1/hla/variant/<variant>')
def get_by_alt(variant):
    limit, page = _parse_pagination()
    return get_dao().get_by_variant(variant, limit=limit, page=page)
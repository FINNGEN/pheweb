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

from .model import HLASummaryDAO, JeevesContext

hla_summary = Blueprint("pheweb_hla_summary", __name__)
development = Blueprint("development", __name__)


app.jeeves: JeevesContext  # type: ignore


def get_dao(current_app=app) -> HLASummaryDAO:
    """ "
    Get DAO.

    Get DAO object stored in jeeves.
    Return 404 if not available as
    it means the HLA Summary data is not
    available.
    """
    dao: typing.Optional[HLASummaryDAO] = current_app.jeeves.hla_summary_dao
    if dao is None:
        result = None
        abort(404, "HLA Summary data not available")
    else:
        result = dao
    return result


@hla_summary.route('/api/v1/hla_summary/top')
def top_data():
    return get_dao().get_top_results()

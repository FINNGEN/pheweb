from flask_login import current_user
from flask import jsonify, request, redirect, session, url_for, g
from ..conf_utils import conf
from .group_based_auth import verify_membership

def _is_api_request() -> bool:
    """Return True for fetch/XHR API calls that cannot follow OAuth redirects."""
    return request.path.startswith('/api/')


def before_request():

    if not conf.authentication:
        print('anonymous visited {!r}'.format(request.path))
        return None
    elif getattr(g, 'is_test', None) is True:
        return None
    elif current_user.is_anonymous:
        session['original_destination'] = request.path
        if _is_api_request():
            return jsonify({'status': 'error', 'message': 'not authenticated'}), 401
        return redirect(url_for('get_authorized',
                                _scheme='https',
                                _external=True))
    elif not verify_membership(current_user.email):
        print('{} is unauthorized and visited {!r}'.format(current_user.email, request.path))
        session['original_destination'] = request.path
        if _is_api_request():
            return jsonify({'status': 'error', 'message': 'not authorized'}), 403
        return redirect(url_for('get_authorized',
                                _scheme='https',
                                _external=True))
    else:
        print('{} visited {!r}'.format(current_user.email, request.path))
        return None

# see discussion
# https://stackoverflow.com/questions/13428708/best-way-to-make-flask-logins-login-required-the-default
def is_public(function):
    function.is_public = True
    return function

def do_check_auth(app):
    # check if endpoint is mapped then
    # check if endpoint has is public annotation
    if request.endpoint and (request.endpoint in app.view_functions) and getattr(app.view_functions[request.endpoint], 'is_public', False) :
        result = None
    else: # check authentication
        result = before_request()
    return result

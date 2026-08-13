# -*- coding: utf-8 -*-

"""
Unit tests for server_auth module.

See: pheweb/serve/server_auth.py
"""
from types import SimpleNamespace

import pytest
from flask import Flask, session, g

from pheweb.serve import server_auth
from pheweb.serve.server_auth import (
    _is_api_request,
    before_request,
    is_public,
    do_check_auth,
)


@pytest.fixture(name="app")
def fixture_app():
    """A minimal app with the one route before_request() redirects to."""
    app = Flask(__name__)
    app.secret_key = "test-secret"

    @app.route("/get_authorized")
    def get_authorized():
        return "ok"

    return app


def _anonymous_user():
    return SimpleNamespace(is_anonymous=True)


def _authenticated_user(email="user@finngen.fi"):
    return SimpleNamespace(is_anonymous=False, email=email)


@pytest.fixture(autouse=True)
def _default_conf(monkeypatch):
    """Auth is on by default; individual tests override as needed."""
    monkeypatch.setattr(server_auth.conf, "authentication", True)


# --- _is_api_request -----------------------------------------------------

def test_is_api_request_true(app):
    with app.test_request_context("/api/drugs/ABC"):
        assert _is_api_request() is True


def test_is_api_request_false(app):
    with app.test_request_context("/variant/1-2-A-G"):
        assert _is_api_request() is False


# --- before_request --------------------------------------------------------

def test_before_request_allows_all_when_auth_disabled(app, monkeypatch):
    monkeypatch.setattr(server_auth.conf, "authentication", False)
    monkeypatch.setattr(server_auth, "current_user", _anonymous_user())
    with app.test_request_context("/variant/1-2-A-G"):
        assert before_request() is None


def test_before_request_allows_test_requests(app, monkeypatch):
    monkeypatch.setattr(server_auth, "current_user", _anonymous_user())
    with app.test_request_context("/variant/1-2-A-G"):
        g.is_test = True
        assert before_request() is None


def test_before_request_anonymous_user_redirected(app, monkeypatch):
    monkeypatch.setattr(server_auth, "current_user", _anonymous_user())
    with app.test_request_context("/variant/1-2-A-G"):
        response = before_request()
        assert response.status_code == 302
        assert "/get_authorized" in response.location
        assert session["original_destination"] == "/variant/1-2-A-G"


def test_before_request_anonymous_api_request_gets_401(app, monkeypatch):
    monkeypatch.setattr(server_auth, "current_user", _anonymous_user())
    with app.test_request_context("/api/drugs/ABC"):
        body, status = before_request()
        assert status == 401
        assert body.get_json() == {"status": "error", "message": "not authenticated"}
        # the destination is still recorded, even though this request can't follow a redirect
        assert session["original_destination"] == "/api/drugs/ABC"


def test_before_request_unauthorized_member_redirected(app, monkeypatch):
    monkeypatch.setattr(server_auth, "current_user", _authenticated_user())
    monkeypatch.setattr(server_auth, "verify_membership", lambda email: False)
    with app.test_request_context("/variant/1-2-A-G"):
        response = before_request()
        assert response.status_code == 302
        assert "/get_authorized" in response.location
        assert session["original_destination"] == "/variant/1-2-A-G"


def test_before_request_unauthorized_api_request_gets_403(app, monkeypatch):
    monkeypatch.setattr(server_auth, "current_user", _authenticated_user())
    monkeypatch.setattr(server_auth, "verify_membership", lambda email: False)
    with app.test_request_context("/api/drugs/ABC"):
        body, status = before_request()
        assert status == 403
        assert body.get_json() == {"status": "error", "message": "not authorized"}


def test_before_request_authorized_member_allowed(app, monkeypatch):
    monkeypatch.setattr(server_auth, "current_user", _authenticated_user())
    monkeypatch.setattr(server_auth, "verify_membership", lambda email: True)
    with app.test_request_context("/variant/1-2-A-G"):
        assert before_request() is None


def test_before_request_authorized_member_api_request_allowed(app, monkeypatch):
    monkeypatch.setattr(server_auth, "current_user", _authenticated_user())
    monkeypatch.setattr(server_auth, "verify_membership", lambda email: True)
    with app.test_request_context("/api/drugs/ABC"):
        # a logged-in, authorized member's API request should pass straight
        # through: no redirect, no error response, and no destination stashed
        # in the session since there's nothing to send them back to.
        assert before_request() is None
        assert "original_destination" not in session


# --- is_public / do_check_auth ---------------------------------------------

def test_is_public_marks_function_and_returns_it_unchanged():
    def view():
        return "hi"

    marked = is_public(view)
    assert marked is view
    assert marked.is_public is True


def test_do_check_auth_skips_before_request_for_public_endpoints(app, monkeypatch):
    @app.route("/public")
    @is_public
    def public_view():
        return "hi"

    # Even though this would normally be denied, a public endpoint must
    # bypass before_request() entirely.
    monkeypatch.setattr(server_auth, "current_user", _anonymous_user())
    with app.test_request_context("/public"):
        assert do_check_auth(app) is None


def test_do_check_auth_checks_non_public_endpoints(app, monkeypatch):
    @app.route("/private")
    def private_view():
        return "hi"

    monkeypatch.setattr(server_auth, "current_user", _anonymous_user())
    with app.test_request_context("/private"):
        response = do_check_auth(app)
        assert response.status_code == 302


def test_do_check_auth_with_unmapped_endpoint_still_checks_auth(app, monkeypatch):
    monkeypatch.setattr(server_auth, "current_user", _anonymous_user())
    with app.test_request_context("/no-such-route"):
        # request.endpoint is None here since no route matched.
        response = do_check_auth(app)
        assert response.status_code == 302

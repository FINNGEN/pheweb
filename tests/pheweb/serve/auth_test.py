# -*- coding: utf-8 -*-

"""
Unit tests for auth module.

See: pheweb/serve/auth.py
"""
from unittest.mock import MagicMock

import pytest
from flask import Flask, session

from pheweb.serve import auth as auth_module
from pheweb.serve.auth import GoogleSignIn

GOOGLE_DISCOVERY_DOC = {
    "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
    "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
    "token_endpoint": "https://oauth2.googleapis.com/token",
}


@pytest.fixture(name="app")
def fixture_app():
    app = Flask(__name__)
    app.secret_key = "test-secret"

    @app.route("/callback/google")
    def oauth_callback_google():
        return "ok"

    return app


@pytest.fixture(autouse=True)
def _conf_login(monkeypatch):
    monkeypatch.setattr(
        auth_module.conf,
        "login",
        {
            "GOOGLE_LOGIN_CLIENT_ID": "test-client-id",
            "GOOGLE_LOGIN_CLIENT_SECRET": "test-client-secret",
        },
        raising=False,
    )

def _bare_sign_in():
    """
    A GoogleSignIn instance with __init__ skipped, for tests that only
    exercise authorize()/callback()/get_callback_url() and want to control
    `.service` directly rather than building a real OAuth2Service.
    """
    instance = GoogleSignIn.__new__(GoogleSignIn)
    instance.service = MagicMock()
    return instance

# --- get_callback_url -------------------------------------------------------

def test_get_callback_url(app):
    sign_in = _bare_sign_in()
    with app.test_request_context("/"):
        url = sign_in.get_callback_url()
    assert url.startswith("https://")
    assert url.endswith("/callback/google")


# --- authorize ---------------------------------------------------------------

def test_authorize_redirects_to_google_and_stores_state(app):
    sign_in = _bare_sign_in()
    sign_in.service.get_authorize_url.return_value = "https://accounts.google.com/auth?foo=bar"

    with app.test_request_context("/"):
        response = sign_in.authorize()
        assert response.status_code == 302
        assert response.location == "https://accounts.google.com/auth?foo=bar"

        stored_state = session["oauth_state"]
        assert stored_state

    kwargs = sign_in.service.get_authorize_url.call_args.kwargs
    assert kwargs["state"] == stored_state
    assert kwargs["scope"] == "email"
    assert kwargs["response_type"] == "code"
    assert kwargs["prompt"] == "select_account"
    assert kwargs["redirect_uri"].endswith("/callback/google")


def test_authorize_uses_a_fresh_state_each_call(app):
    sign_in = _bare_sign_in()
    sign_in.service.get_authorize_url.return_value = "https://accounts.google.com/auth"

    with app.test_request_context("/"):
        sign_in.authorize()
        state_1 = session["oauth_state"]

    with app.test_request_context("/"):
        sign_in.authorize()
        state_2 = session["oauth_state"]

    assert state_1 != state_2


# --- callback ------------------------------------------------------------------

def test_callback_without_code_returns_none(app):
    sign_in = _bare_sign_in()
    with app.test_request_context("/callback/google"):
        assert sign_in.callback() == (None, None)


def test_callback_rejects_missing_session_state(app):
    """No prior authorize() call means no expected state was ever stored."""
    sign_in = _bare_sign_in()
    with app.test_request_context("/callback/google?code=abc123&state=whatever"):
        assert sign_in.callback() == (None, None)


def test_callback_rejects_mismatched_state(app):
    """Guards against CSRF: a forged callback with the wrong state must be rejected."""
    sign_in = _bare_sign_in()
    with app.test_request_context("/callback/google?code=abc123&state=wrong"):
        session["oauth_state"] = "expected"
        assert sign_in.callback() == (None, None)
        # the stored state is single-use, consumed even on a failed attempt
        assert "oauth_state" not in session


def test_callback_with_valid_state_returns_name_and_email(app):
    sign_in = _bare_sign_in()
    userinfo_response = MagicMock()
    userinfo_response.json.return_value = {"name": "Alice", "email": "alice@finngen.fi"}
    oauth_session = MagicMock()
    oauth_session.get.return_value = userinfo_response
    sign_in.service.get_auth_session.return_value = oauth_session

    with app.test_request_context("/callback/google?code=abc123&state=expected"):
        session["oauth_state"] = "expected"
        result = sign_in.callback()

    assert result == ("Alice", "alice@finngen.fi")
    call_kwargs = sign_in.service.get_auth_session.call_args.kwargs
    assert call_kwargs["data"]["code"] == "abc123"
    assert call_kwargs["data"]["grant_type"] == "authorization_code"
    assert call_kwargs["data"]["redirect_uri"].endswith("/callback/google")


def test_callback_falls_back_to_email_when_name_missing(app):
    sign_in = _bare_sign_in()
    userinfo_response = MagicMock()
    userinfo_response.json.return_value = {"email": "bob@finngen.fi"}
    oauth_session = MagicMock()
    oauth_session.get.return_value = userinfo_response
    sign_in.service.get_auth_session.return_value = oauth_session

    with app.test_request_context("/callback/google?code=abc123&state=expected"):
        session["oauth_state"] = "expected"
        result = sign_in.callback()

    assert result == ("bob@finngen.fi", "bob@finngen.fi")

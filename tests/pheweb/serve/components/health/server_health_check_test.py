import pytest
from flask import Flask
from pheweb.serve.components.health.server_health_check import HomepageCheck
from pheweb.serve.server import app
def test_error_health() -> None:
    app_context = app.app_context()
    app_context.push()
    with app_context:
        check = HomepageCheck()
        assert None == check.get_status()
    app_context.pop()

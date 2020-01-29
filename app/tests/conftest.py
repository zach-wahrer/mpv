import pytest
from flask import app as flask_app
from app import create_app


@pytest.fixture
def app() -> flask_app:
    app = create_app(test_config="app.tests.test_config")
    return app

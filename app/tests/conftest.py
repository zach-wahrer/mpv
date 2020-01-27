import pytest
from flask import app as flask_app
from app import create_app


@pytest.fixture
def app() -> flask_app:
    app = create_app()
    app.config['TESTING'] = True
    app.config['MP_DEV'] = True
    return app

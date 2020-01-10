import pytest
import requests
from mysql.connector import CMySQLConnection, Error, MySQLConnection

from .test_data.mp_api_response import test_user_data
from ..helpers.database_connection import db_connect, db_close
from ..helpers.mountain_project import MountainProjectHandler


def test_connect(app: pytest.fixture) -> None:
    """Asserts the database connection is made, closes and confirms closed connection."""
    with app.app_context():
        connection = db_connect(config=app.config)
        assert connection.autocommit
        assert connection.is_connected()
        assert isinstance(connection, (MySQLConnection, CMySQLConnection))

        cursor = connection.cursor()
        db_close(cursor, connection)
        assert connection.is_connected() is False


def test_failed_db_connection() -> None:
    """Asserts that errors raised during the connection process due to improper config values are caught."""
    with pytest.raises(Error):
        db_connect(config={})


class MockResponse:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def fetch_user():
        # Lets return a mock Response object so we can later call .json()
        return requests.models.Response

    @staticmethod
    def json():
        # Instead of actually decoding the Response object, return our test data.
        return test_user_data


def test_prod_env_mp_handler(monkeypatch):
    """Any arguments may be passed and mocked functions will always return our mocked objects."""
    def mock_get(*args, **kwargs):
        # Returns an empty requests.Response object
        return MockResponse().fetch_user()

    def mock_json(*args, **kwargs):
        # When Response.json() is called, return our test data instead of decoding JSON.
        return test_user_data

    # apply the monkeypatch for requests.get to mock_get()
    monkeypatch.setattr(requests, "get", mock_get)
    # apply the monkeypatch for requests.models.Response to mock_json()
    monkeypatch.setattr(requests.models.Response, "json", mock_json)

    api = MountainProjectHandler(email="test_email@example.com", api_key='test_key', dev_env=False)
    # api.fetch_user, which contains requests.get(), uses monkeypatch
    api.fetch_user()
    # api.parse_user_data(), which contains Response.json(), uses monkeypatch.
    data = api.parse_user_data()
    assert data['mp_id'] == 105324100
    assert data["name"] == "Test User"
    assert data["status"] == 0


def test_dev_env_mp_handler():
    api = MountainProjectHandler(email="test_email@example.com", api_key='test_key', dev_env=True)
    result = api.fetch_user()
    assert result["name"] == "Dev"
    assert result["id"] == 1111
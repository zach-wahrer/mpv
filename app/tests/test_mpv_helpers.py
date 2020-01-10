import encodings

import pytest
import requests
from mysql.connector import CMySQLConnection, Error, MySQLConnection

from .test_data.mp_api_response import test_expected_data, test_ticks_response, test_user_data
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
    """Handles mocking requests, and feeds mock data to tests requiring external API data."""
    def __call__(self):
        return requests.models.Response

    @staticmethod
    def json():
        return test_user_data

    @property
    def content(self):
        return test_ticks_response


def test_prod_env_mp_handler(monkeypatch):
    """Any arguments may be passed and mocked functions will always return our mocked objects."""
    def mock_get(*args, **kwargs):
        # Returns an empty requests.Response object
        return MockResponse()

    def mock_json(*args, **kwargs):
        # When Response.json() is called, return our test data instead of actually calling that method.
        return MockResponse().json()

    def mock_content(*args, **kwargs):
        # When Response.content is called return our MockResponse content property.
        return MockResponse().content

    # apply the monkeypatch's
    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests.models.Response, "json", mock_json)
    monkeypatch.setattr(requests.models.Response, "content", mock_content)

    # Create MountainProjectHandler instance which will use monkeypatch and test data.
    api = MountainProjectHandler(email="test_email@example.com", api_key='test_key', dev_env=False)
    api.fetch_user()
    data = api.parse_user_data()

    # Make assertions of returned data from MountainProjectParser.
    assert data["mp_id"] == 105324100
    assert data["name"] == "Test User"
    assert data["status"] == 0

    # Fetch the mock mock tick list
    api.fetch_tick_list()
    data = api.parse_tick_list()

    # Assert data output is what we expect
    assert data["status"] == 0
    assert data["data"] == test_expected_data


def test_dev_env_mp_handler():
    # dev_env=True, so simply assert returned data matches _DEV_USER_DATA
    api = MountainProjectHandler(email="test_email@example.com", api_key='test_key', dev_env=True)
    response = api.fetch_user()
    assert response["name"] == "Dev"
    assert response["mp_id"] == 1111

    # assert MountainProjectParser simply returns the desired response.
    result = api.parse_user_data(dev_env=True)
    assert result['mp_id'] == 1111
    assert result["name"] == "Dev"
    assert result["status"] == 0

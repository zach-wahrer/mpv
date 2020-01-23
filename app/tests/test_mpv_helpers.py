from typing import Dict

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from mysql.connector import CMySQLConnection, MySQLConnection

from .test_data.mp_api_response import test_expected_data, test_processed_csv, test_ticks_response, test_user_data
from ..errors import *
from ..helpers.database_connection import db_connect, db_close
from ..helpers.mountain_project import MountainProjectHandler


class TestDatabaseHelpers:
    def test_connect(self, app):
        """Asserts the database connection is made, closes and confirms closed connection."""
        connection = db_connect(config=app.config)
        assert connection.autocommit
        assert connection.is_connected()
        assert isinstance(connection, (MySQLConnection, CMySQLConnection))

        cursor = connection.cursor()
        db_close(cursor, connection)
        assert connection.is_connected() is False

    def test_failed_db_connection(self) -> None:
        """Asserts that errors raised during the connection process due to improper config values are caught."""
        with pytest.raises(DatabaseException):
            db_connect(config={})


class MockResponse:
    """Mocks a requests.get() response, and feeds mock data to functions requiring external API data."""
    @staticmethod
    def json() -> Dict:
        return test_user_data

    @property
    def content(self) -> bytes:
        return test_ticks_response


class TestMountainProjectHandler:
    @classmethod
    def setup_class(cls):
        # Create MountainProjectHandler instances which will use monkeypatch and test data.
        cls.api_dev = MountainProjectHandler(email="test@example.com", api_key="", dev_env=True)
        cls.api_prod = MountainProjectHandler(email="test_email@example.com", api_key='test_key', dev_env=False)

        cls.monkeypatch = MonkeyPatch()
        cls.monkeypatch.setattr(requests, "get", cls.mock_get)  # Apply monkeypatch to requests.get()

    @staticmethod
    def mock_get(*args, **kwargs) -> MockResponse:
        """
        When requests.get() is called, return our MockResponse object.
        This includes access to all MockResponse methods and properties.
        """
        return MockResponse()

    def test_mp_api_user_data(self) -> None:
        """Confirms fetching and parsing logic of data from Mountain Project API"""
        self.api_prod.fetch_user()
        data = self.api_prod.parse_user_data()

        # Assertions of returned data from MountainProjectParser.
        assert data["mp_id"] == 105324100
        assert data["name"] == "Test User"
        assert data["status"] == 0

    def test_mp_api_user_ticks(self) -> None:
        """Confirms fetching and processing of ticklist csv returns expected output."""
        self.api_prod.fetch_tick_list()
        data = self.api_prod.parse_tick_list()

        assert data["status"] == 0
        assert data["data"] == test_expected_data

    def test_mp_dev_env_user_data(self) -> None:
        """dev_env=True, so simply assert returned data matches _DEV_USER_DATA"""
        response = self.api_dev.fetch_user()
        assert response["name"] == "Dev"
        assert response["mp_id"] == 1111

    def test_mp_dev_env_parse_user_data(self) -> None:
        """dev_env=True, so simply assert returned data is what we expect from parse_data()"""
        data = self.api_dev.parse_user_data(dev_env=True)
        assert data['mp_id'] == 1111
        assert data["name"] == "Dev"
        assert data["status"] == 0

    def test_mp_dev_env_ticks(self) -> None:
        """When dev is True we expect to return None instead of making a request."""
        assert self.api_dev.fetch_tick_list() is None

    def test_mp_dev_env_parse_ticks(self) -> None:
        """Ensure when dev_env=True that the processed test_ticks.csv file is the output of parse_tick_list()"""
        data = self.api_dev.parse_tick_list(dev_env=True)
        assert data["status"] == 0
        assert data["data"] == test_processed_csv

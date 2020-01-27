from typing import Dict

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from requests import HTTPError

from ..errors.exeptions import *


class MockResponse:
    @staticmethod
    def json() -> Dict:
        return {}


class TestErrorHandlers:
    @staticmethod
    def raise_http_error(*args, **kwargs):
        raise HTTPError

    @staticmethod
    def mock_get_response(*args, **kwargs) -> MockResponse:
        """When MonkeyPatching a requests.get() call, return a MockResponse object."""
        return MockResponse()

    def test_404(self, app: pytest.fixture) -> None:
        """
        Makes a GET request to a non-existent endpoint. Confirms the correct response status code is returned
        and that the application handles the error while returning a safe response message to the client.
        """
        client = app.test_client()
        response = client.get('/not_a_page')
        data = response.data.decode("utf-8")
        msg = "The requested URL was not found on the server. If you entered the URL manually please check your " \
              "spelling and try again."

        assert response.status == "404 NOT FOUND"
        assert msg in data

    def test_mountain_project_api_exception(self, app: pytest.fixture) -> None:
        """Confirms the correct response status and safe error message of MPAPIException."""
        monkeypatch = MonkeyPatch()
        monkeypatch.setattr(requests, "get", self.mock_get_response)
        client = app.test_client()
        app.config["MPV_DEV"] = False  # dev_env to False so a mocked request will be made.
        response = client.post("/data")

        assert response.status == "403 FORBIDDEN"
        assert MPAPIException.msg in response.data.decode("utf-8")

    def test_request_exception(self, app: pytest.fixture) -> None:
        """Confirms the correct response status and safe error message of RequestException."""
        monkeypatch = MonkeyPatch()
        monkeypatch.setattr(requests, "get", self.raise_http_error)
        client = app.test_client()
        app.config["MPV_DEV"] = False  # dev_env to False so a mocked request will be made.
        response = client.post("/data")

        assert response.status == "400 BAD REQUEST"
        assert RequestException.msg in response.data.decode("utf-8")

    def test_database_exception(self, app: pytest.fixture) -> None:
        """
        Confirms the correct response status and safe error message of DatabaseException. The test config settings
        do not have database credentials, therefore an error will be raised when the attempting to process test user
        data.
        """
        client = app.test_client()
        response = client.post("/data", data={'test': 'yes'})

        assert response.status == "503 SERVICE UNAVAILABLE"
        assert DatabaseException.msg in response.data.decode("utf-8")

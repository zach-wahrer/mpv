import requests
from _pytest.monkeypatch import MonkeyPatch
from requests import HTTPError

from ..errors.exeptions import *


class TestErrorHandlers:
    @staticmethod
    def mock_get(*args, **kwargs):
        raise HTTPError

    def test_404(self, app):
        with app.test_client() as client:
            response = client.get('/notapage')
        data = response.data.decode("utf-8")
        assert 'Error' in data
        msg = "The requested URL was not found on the server. If you entered the URL manually please check your " \
              "spelling and try again."

        assert msg in data

    def test_mountain_project_api_exception(self, app):
        with app.test_client() as client:
            response = client.post('/data')
        data = response.data.decode("utf-8")
        assert MPAPIException.msg in data

    def test_request_exception(self, app):
        monkeypatch = MonkeyPatch()
        monkeypatch.setattr(requests, "get", self.mock_get)
        with app.test_client() as client:
            response = client.post("/data")
        data = response.data.decode("utf-8")
        assert RequestException.msg in data

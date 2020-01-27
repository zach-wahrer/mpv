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
            response = client.get('/not_a_page')
        data = response.data.decode("utf-8")
        assert response.status == "404 NOT FOUND"
        msg = "The requested URL was not found on the server. If you entered the URL manually please check your " \
              "spelling and try again."

        assert msg in data

    def test_mountain_project_api_exception(self, app):
        app.config["MPV_DEV"] = False
        with app.test_client() as client:
            app.config["MP_DEV"] = False
            response = client.post("/data")
        data = response.data.decode("utf-8")
        assert response.status == "403 FORBIDDEN"
        assert MPAPIException.msg in data

    def test_request_exception(self, app):
        app.config["MPV_DEV"] = False
        print(app.config)
        monkeypatch = MonkeyPatch()
        monkeypatch.setattr(requests, "get", self.mock_get)
        with app.test_client() as client:
            response = client.post("/data")
        assert response.status == "400 BAD REQUEST"
        data = response.data.decode("utf-8")
        assert RequestException.msg in data

    def test_database_exception(self, app):
        app.config["MYSQL_USER"] = None
        data = {'test': 'yes'}
        with app.test_client() as client:
            response = client.post("/data", data=data)
        assert response.status == "503 SERVICE UNAVAILABLE"
        data = response.data.decode("utf-8")
        assert DatabaseException.msg in data

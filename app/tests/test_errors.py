import pytest

from ..errors.error_registry import ExceptionRegistry


class TestErrorHandlers:
    def test_all(self, app: pytest.fixture):

        client = app.test_client()

        @app.route('/test_exception')
        def test_exception():
            raise e.value
        for e in ExceptionRegistry:
            response = client.get('/test_exception')
            assert str(e.value.status_code) in response.status
            assert e.value.msg in response.data.decode()

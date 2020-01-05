import pytest


def test_index(client: pytest.fixture) -> None:
    """Assert that a status code of 200 is returned from /"""
    index = client.get('/')
    assert index.status == '200 OK'

import os
import tempfile

import pytest

from app import create_app


@pytest.fixture
def client():
    """Called from any test that passes client as an argument."""
    app = create_app()
    # Set the database value to an empty tempfile. This can be changed or overridden if testing against the actual
    # database is necessary.
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_index(client):
    """Assert that a status code of 200 is returned from /"""
    index = client.get('/')
    assert index.status == '200 OK'


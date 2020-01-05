"""
Puts any fixture functions into a separate file so that tests from multiple test modules in the directory
can access the fixture functions.
https://docs.pytest.org/en/latest/fixture.html
"""

import os
import tempfile

import pytest

from app import create_app


@pytest.fixture
def client():
    # First lets create an instance of our application.
    app = create_app()
    # Set the database value to an empty tempfile. This can be changed or overridden if testing against the actual
    # database is necessary.
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

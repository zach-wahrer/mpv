from mysql.connector import CMySQLConnection, Error, MySQLConnection
from pytest import fixture, raises

from ..helpers.database_connection import db_connect, db_close
from ..helpers.mountain_project import MountainProjectApi


def test_connect(app: fixture) -> None:
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
    with raises(Error):
        db_connect(config={})


"""def test_mp_request(app: fixture) -> None:
    mp = MountainProjectApi()
    email = mp.lookup_user(email=app.config.get("TEST_ACCT"), api_key=app.config.get("MP_KEY"))
    print(email)
    assert 1 == 1

def test_ticklist(app):
    mp = MountainProjectApi()
    ticks = mp.lookup_ticklist(username='Ostrich Society', mp_id='107324100')
    print(ticks.content.decode('utf-8'))
    assert 1 == 1
"""
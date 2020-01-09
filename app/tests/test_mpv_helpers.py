from mysql.connector import CMySQLConnection, Error, MySQLConnection
from pytest import fixture, raises

from ..helpers.database_connection import db_connect, db_close
from ..helpers.mountain_project import MountainProjectHandler


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


def test_mp_request(app: fixture) -> None:
    api = MountainProjectHandler(email='benjpalmer@yahoo.com', api_key=app.config.get("MP_KEY"))
    api.fetch_user()
    print(api.parse_user_data())
    assert 1 == 1

    api.fetch_tick_list()
    print(api.parse_tick_list())

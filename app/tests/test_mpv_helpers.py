from mysql.connector import CMySQLConnection, Error, MySQLConnection
from pytest import fixture, raises

from ..helpers.database_connection import db_connect, db_close


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

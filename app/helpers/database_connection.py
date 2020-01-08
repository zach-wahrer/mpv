from typing import Dict, Union

from mysql.connector import connect, Error, MySQLConnection, CMySQLConnection


def db_connect(config: Dict) -> Union[MySQLConnection, CMySQLConnection]:
    """Create connection to database."""
    try:
        connection = connect(
            host=config.get("MYSQL_ADDRESS"), database=config.get("MYSQL_TABLE"),
            user=config.get("MYSQL_USER"), password=config.get("MYSQL_PASSWD"))
        connection.autocommit = True
        return connection
    except (AttributeError, Error, NameError) as e:
        raise e


def db_close(cursor: MySQLConnection.cursor, connection: Union[MySQLConnection, CMySQLConnection]) -> None:
    """Close down the database connection."""
    cursor.close()
    connection.close()

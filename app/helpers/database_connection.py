from typing import Dict, Union

from mysql.connector import connect, Error, MySQLConnection, CMySQLConnection

from ..errors.exeptions import DatabaseException


def db_connect(config: Dict) -> Union[MySQLConnection, CMySQLConnection]:
    """Create connection to database."""
    try:
        connection = connect(
            host=config.get("MYSQL_ADDRESS"), database=config.get("MYSQL_TABLE"),
            user=config.get("MYSQL_USER"), password=config.get("MYSQL_PASSWD"))
    except (AttributeError, Error, NameError):
        raise DatabaseException

    connection.autocommit = True
    return connection
    

def db_close(cursor: MySQLConnection.cursor, connection: Union[MySQLConnection, CMySQLConnection]) -> None:
    """Close down the database connection."""
    cursor.close()
    connection.close()


def db_load(userid, data, config=None):
    """Load CSV file into MySQL database."""
    # Connect to database
    try:
        connection = db_connect(config=config)
        cursor = connection.cursor()

        # Drop current user table if it exists
        cursor.execute("SHOW TABLES LIKE '%s';", (userid,))
        if cursor.fetchone():
            cursor.execute("DROP TABLE `%s`;", (userid,))

        # Create new user table
        create = """CREATE TABLE `%s`(
            `id` MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
            `date` DATE NOT NULL,
            `name` CHAR(100) CHARACTER SET utf8 NOT NULL,
            `pitches` SMALLINT UNSIGNED NOT NULL,
            `style` TINYINT UNSIGNED NULL,
            `lead_style` TINYINT UNSIGNED NULL,
            `type` VARCHAR(18) CHARACTER SET utf8 NOT NULL,
            `height` MEDIUMINT UNSIGNED NULL,
            `code` MEDIUMINT UNSIGNED NOT NULL,
            PRIMARY KEY(`id`))"""
        cursor.execute(create, (userid,))

        # Get value pairs for index tables
        pairs = get_pairs(cursor)

        # Load data into table
        for row in data:
            make_sql_insert(cursor, pairs, userid, row)

        # Close database
        db_close(cursor, connection)
        # Return success
        return

    # Handle database errors if they occur
    except Error as e:
        db_close(cursor, connection)
        raise DatabaseException


def get_pairs(cursor):
    """Get index/value pair route data identifiers from MySQL tables."""
    # Set the tables to grab data from
    tables = ("style", "lead_style", "type")
    pairs = dict()
    select = "SELECT * FROM `%s`;"
    # Loop through each of the tables
    for i in tables:
        cursor.execute(select % (i,))
        # Build the dictionary
        pairs[i] = dict()
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            pairs[i][row[1]] = row[0]

    return pairs


def make_sql_insert(cursor, pairs, userid, row):
    """Insert individual ticks into database."""
    insert = """INSERT INTO `%s` (`date`, `name`, `pitches`, `style`,
        `lead_style`, `type`, `height`, `code`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
    # Find the right id in each dictionary
    s_id = pairs["style"].get(row[3])
    ls_id = pairs["lead_style"].get(row[4])

    # Special processing for csv values in type
    if row[5]:
        t_id = pairs["type"].get(row[5])
        # This runs if there is no match found, ie. var is multi-type
        if t_id is None:
            t_id = ""
            # Thanks Sean Vieira for this list comprehension
            # (via StackOverflow)
            split = [x.strip() for x in row[5].split(',')]
            # Build the id field as a csv
            for i in split:
                t_id += str(pairs["type"].get(i))
                t_id += ","
            t_id = t_id[:-1]
    # Assign blank id if type import is blank
    else:
        t_id = pairs["type"].get("Blank")

    # Make correction for 0000-00-00 date
    if row[0] == "0000-00-00" or not row[0]:
        # Set date to the Mountain Project default value for null date
        date = "1969-12-31"
    else:
        date = row[0]

    # Make correction for blank route name
    if row[1]:
        name = row[1]
    else:
        name = "None"

    # Make correction for blank pitch value
    if row[2]:
        pitches = row[2]
    else:
        pitches = 1

    # Make correction for blank height value
    if row[6]:
        height = row[6]
    else:
        height = None

    # Make correction for blank code value
    if row[7]:
        code = row[7]
    else:
        code = 0

    # Set the values tuple
    values = (userid, date, name, pitches, s_id,
              ls_id, t_id, height, code)

    # Insert the row
    cursor.execute(insert, values)

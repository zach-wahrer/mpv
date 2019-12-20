"""Helper functions for the MPV web app."""

import json
import csv
import requests
import mysql.connector
from mysql.connector import Error

# Open the config file
with open('config.json') as config_file:
    config = json.load(config_file)

# Set database vars
MYSQL_USER = config["MYSQL_USER"]
MYSQL_ADDRESS = config["MYSQL_ADDRESS"]
MYSQL_TABLE = config["MYSQL_TABLE"]
MYSQL_PASSWD = config["MYSQL_PASSWD"]


def db_connect():
    """Create connection to database."""
    connection = mysql.connector.connect(
        host=MYSQL_ADDRESS, database=MYSQL_TABLE,
        user=MYSQL_USER, password=MYSQL_PASSWD)
    connection.autocommit = True
    return connection


def get_userid(email):
    """
    Get username/id using email via MountainProject.com API.

    (https://www.mountainproject.com/data)
    """
    # Check for dev mode
    if config["MPV_DEV"] != "on":
        # Get API Key
        API_KEY = config["MP_KEY"]

        # Get info from MountainProject
        try:
            reply = requests.get(f"https://www.mountainproject.com/data/" +
                                 f"get-user?email={email}&key={API_KEY}")
            reply.raise_for_status()
        except requests.RequestException:
            return {"status": 1, "code": reply.status_code}

        # Parse the reply
        try:
            data = reply.json()
        except (KeyError, TypeError, ValueError):
            return {"status": 2}

        # Format the successful return
        return {"status": 0, "name": data['name'], "id": data['id']}

    # Run in dev mode
    else:
        return {"status": 0, "name": "Dev", "id": 1111}


def ticklist(username, id):
    """
    Download a CSV file of all users ticks from MP, remove unneeded fields.

    i.e. https://www.mountainproject.com/user/106610639/zach-wahrer/tick-export
    """
    # Check for dev mode
    if config["MPV_DEV"] != "on":
        url = (f"https://www.mountainproject.com/user/" +
               f"{id}/{username}/tick-export")
        # Get the csv file
        try:
            download = requests.get(url)
            download.raise_for_status()
        except requests.RequestException:
            return {"status": 1, "code": download.status_code}

        # Decode the file and split it into a csv list
        decoded = download.content.decode('utf-8')
        ticklist = list(csv.reader(decoded.splitlines(), delimiter=','))

    else:
        # Load from file if dev mode active
        csv_file = open('test_ticks.csv')
        ticklist = list(csv.reader(csv_file, delimiter=','))

    # Remove unneeded data fields
    # Delete in reverse order to make field posistions simpler
    remove = [12, 8, 7, 6, 4, 3, 2]
    for row in ticklist:
        for i in remove:
            del row[i]
    # Remove the CSV header
    del ticklist[0]

    return {"status": 0, "data": ticklist}


def db_load(userid, data):
    """Load CSV file into MySQL database."""
    # Connect to database
    try:
        connection = db_connect()
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
        return {"status": 0}

    # Handle database errors if they occur
    except Error as e:
        db_close(cursor, connection)
        return {"status": 1, "error": e}


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
    t_id = pairs["type"].get(row[5])
    if t_id is None:
        t_id = ""
        # Thanks Sean Vieira for this list comprehension (via StackOverflow)
        split = [x.strip() for x in row[5].split(',')]
        # Build the id field as a csv
        for i in split:
            t_id += str(pairs["type"].get(i))
            t_id += ","
        t_id = t_id[:-1]

    # Make correction for 0000-00-00 date
    if row[0] == "0000-00-00" or row[0] is None:
        # Set date to the Mountain Project default value for null date
        date = "1969-12-31"
    else:
        date = row[0]

    # Make correction for blank route name
    if row[1] is None:
        name = "None"
    else:
        name = row[1]

    # Make correction for blank pitch value
    if row[2] is None:
        pitches = 1
    else:
        pitches = row[2]

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


def db_close(cursor, connection):
    """Close down the database connection."""
    cursor.close()
    connection.close()

"""Helper functions for the MPV web app."""

import os
import csv
import requests
import mysql.connector
from mysql.connector import Error

# On install, change this line to your MySQL info #
MYSQL_USER = "mpv"
MYSQL_ADDRESS = "localhost"
MYSQL_DATABASE = "mpv"

# Get the MySQL password
if not os.environ.get("MPV_MYSQL_PASSWD"):
    raise RuntimeError("MPV_MYSQL_PASSWD not set")
MYSQL_PASSWD = os.environ.get("MPV_MYSQL_PASSWD")


def get_userid(email):
    """
    Get username/id using email via MountainProject.com API.

    (https://www.mountainproject.com/data)
    """
    # Get API Key
    API_KEY = os.environ.get("MPV_MP_KEY")

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


def ticklist(username, id):
    """
    Download a CSV file of all users ticks from MP, remove unneeded fields.

    i.e. https://www.mountainproject.com/user/106610639/zach-wahrer/tick-export
    """
    # REMOVE COMMENTING BELOW TO ENABLE DOWNLOADS FROM MP
    # url = f"https://www.mountainproject.com/user/{id}/{username}/tick-export"

    # # Get the csv file
    # try:
    #     download = requests.get(url)
    # except requests.RequestException:
    #     return [1, reply.status_code]
    #
    # # Decode the file and split it into a csv list
    # decoded = download.content.decode('utf-8')
    # ticklist = list(csv.reader(decoded.splitlines(), delimiter=','))

    # LOAD FROM FILE TO DECREASE UNNEEDED TEST TRAFFIC TO MP
    # REMOVE ONCE READY TO GO LIVE
    csv_file = open('test_ticks.csv')
    ticklist = list(csv.reader(csv_file, delimiter=','))

    # Remove unneded data fields
    # Delete in reverse order to make field posistions simpler
    remove = [12, 8, 7, 6, 4, 3]
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
        connection = mysql.connector.connect(
            host=MYSQL_ADDRESS, database=MYSQL_DATABASE,
            user=MYSQL_USER, password=MYSQL_PASSWD)

        if connection.is_connected():
            # Initialize the cursor
            connection.autocommit = True
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
                `grade` VARCHAR(50) CHARACTER SET utf8 NOT NULL,
                `pitches` SMALLINT UNSIGNED NOT NULL,
                `style` TINYINT UNSIGNED NULL,
                `lead_style` TINYINT UNSIGNED NULL,
                `type` VARCHAR(18) CHARACTER SET utf8 NOT NULL,
                `height` SMALLINT UNSIGNED NULL,
                `code` MEDIUMINT UNSIGNED NOT NULL,
                PRIMARY KEY(`id`))"""
            cursor.execute(create, (userid,))

            # Load data into table
            tmp = "try2"
            # for row in data:
            insert = """INSERT INTO `%s` (`date`, `name`, `grade`,
                `pitches`, `style`, `lead_style`, `type`, `height`,
                `code`) VALUES ('2019-11-11', %s, '5.10', '1', NULL, NULL,
                '1', '50', '10000');"""
            cursor.execute(insert, (userid, tmp))
            # Close database
            cursor.close()
            connection.close()

            return {"status": 0}

    # Handle database errors if they occur
    except Error as e:
        cursor.close()
        connection.close()
        return {"status": 1, "error": e}

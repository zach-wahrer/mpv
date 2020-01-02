"""Check that the database has appropriate tables for MPV, add them if not."""

import csv

import mysql.connector
from mysql.connector import Error

from ..config import *


def main():
    # Connect to database
    try:
        connection = mysql.connector.connect(
            host=MYSQL_ADDRESS, database=MYSQL_TABLE,
            user=MYSQL_USER, password=MYSQL_PASSWD)

        # Initialize the cursor
        connection.autocommit = True
        cursor = connection.cursor()

        # Search for required tables
        req_tables = [MYSQL_TABLE, 'style', 'lead_style', 'type', 'code']
        select = """SELECT table_name FROM information_schema.tables WHERE
                 table_schema = %s AND table_name IN (%s, %s, %s, %s);"""

        cursor.execute(select, req_tables)

    except Error as e:
        print(e)
        close_db_exit(cursor, connection)

    # Set up next variable query to create tables
    create = """CREATE TABLE `%s`(
        `id` MEDIUMINT UNSIGNED NOT NULL %s,
        `%s` CHAR(12) NOT NULL, PRIMARY KEY(`id`));"""
    # Remove now unneed element for the create/insert loop
    req_tables.pop(0)

    # Add existing MPV MySQL tables to a list
    tables = list()
    for row in cursor.fetchall():
        tables.append(row[0])

    # Loop through required tables, adding them if they aren't in the database
    for i in req_tables:
        if i not in tables:

            # Show user current table operation
            print("Building: " + MYSQL_TABLE + "." + i)
            # Set everything but code to auto AUTO_INCREMENT
            if i == "code":
                auto = ""
            else:
                auto = "AUTO_INCREMENT"

            # Insert the missing table
            # Use % here to keep from single quoting the table names
            try:
                cursor.execute(create % (i, auto, i))
            except Error as e:
                print(e)
                print("db_setup Error: Please delete the added tables" +
                      " and try again.")
                close_db_exit(cursor, connection)
                exit()

            # Populate the specific table
            values = list()
            insert = "INSERT INTO `%s` " % (i)
            if i == "style":
                values = ["Solo", "TR", "Follow", "Lead", "Flash",
                          "Attempt", "Send"]
                insert += "(`style`) VALUES"
            elif i == "lead_style":
                values = ["Onsight", "Flash", "Redpoint", "Pinkpoint",
                          "Fell/Hung"]
                insert += "(`lead_style`) VALUES"
            elif i == "type":
                values = ["Sport", "Trad", "Boulder", "TR", "Aid",
                          "Alpine", "Ice", "Mixed", "Snow", "Blank"]
                insert += "(`type`) VALUES"
            elif i == "code":
                try:
                    csv_file = open('grade_codes.csv')
                except IOError:
                    print("Cannot open grade_codes.csv. Please make sure" +
                          " the file is available, drop the `code`" +
                          " table, and try again.")
                    close_db_exit(cursor, connection)

                pairs = list(csv.reader(csv_file, delimiter=','))
                insert += "(`id`, `code`) VALUES"
                for row in pairs:
                    # Create the id for codes
                    insert += " ('%s', '%s')," % (row[0], row[1])
                # Remove the final comma
                insert = insert[:-1]

            # Do the rest of the query build if it is not the code table
            if i != "code":
                # Create values for the MySQL query
                for value in values:
                    insert += " (%s),"
                # Remove the final comma
                insert = insert[:-1]
                # Insert the values
                try:
                    cursor.execute(insert + ";", values)
                except Error as e:
                    print(e)
                    print("db_setup Error: Please drop the added tables" +
                          "and try again.")
                    close_db_exit(cursor, connection)
            else:
                try:
                    # Insert the values for code tables
                    cursor.execute(insert + ";")
                except Error as e:
                    print(e)
                    print("db_setup Error: Please drop the `code` table" +
                          " and try again.")
                    close_db_exit(cursor, connection)

    print("MPV database successfully configured")
    close_db_exit(cursor, connection)


def close_db_exit(cursor, connection):
    cursor.close()
    connection.close()
    exit()


if __name__ == "__main__":
    main()

"""Graphing functions for the MPV web app."""

from matplotlib.figure import Figure
from helpers import db_connect, db_close
import sys


def test(cursor):
    """Test database connection."""
    cursor.execute("SELECT `id` FROM `style`;")
    values = cursor.fetchall()
    return values


# def kind_of_climber():
#     """Returns the most ticked style of climb."""
#     connection = db_connect()
#     cursor = connection.cursor()

def height_climbed(cursor, userid):
    """Compute total height climbed."""
    select = """SELECT `height`, `type`.`type`, `date` FROM `%s`
            JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`"""
    cursor.execute(select, (userid, userid))
    values = cursor.fetchall()
    # Create total height and yearly values
    total_height = int()
    year_height = dict()
    defaults = {"Aid": 75, "Boulder": 8, "Ice": 100, "Mixed": 100,
                "Snow": 200, "Sport": 75, "TR": 50, "Trad": 150}
    for row in values:
        year = row[2].year
        # Set default heights for when no data is available
        if row[0] is None:
            for key in defaults:
                if row[1] == key:
                    total_height += defaults[key]
                    # Add to Yearly
                    year_height = add_to_year(year, defaults[key], year_height)
        # Otherwise, add it to the total value
        else:
            total_height += row[0]
            # Add to yearly
            year_height = add_to_year(year, row[0], year_height)
    return {"total": total_height, "yearly": year_height}


def add_to_year(year, height, year_height):
    """Add height to a given year."""
    if year in year_height:
        year_height[year] = year_height[year] + height
    else:
        year_height.update({year: height})
    return year_height

"""
A small webapp that functions on MountainProject.com data.

It imports data based on a user ID, then analyzes and displays it.

Code by Zach Wahrer [github.com/zachtheclimber]
and BenfromEarth [github.com/benjpalmer].
"""

import re

from flask import Flask, render_template, request, redirect

from .config import *
from .graphing import height_climbed, pitches_climbed, grade_scatter, get_types
from .helpers import get_userid, ticklist, db_load, db_connect, db_close


def create_app(test_config=None):
    """Create Flask app to generate web controller."""
    app = Flask(__name__)

    # Get config values. If we are in testing env, load the test config.
    if test_config:
        app.config.from_object(test_config)
    else:
        app.config.from_object('app.config')

    @app.route("/", methods=["GET", "POST"])
    def index():
        """Show main user input page."""
        return render_template("index.html")

    @app.route("/data", methods=["GET", "POST"])
    def data():
        """Process input data and output graphs."""
        if request.method == "POST":

            # Check for test link click from input page
            if request.form.get("test") == "yes":
                email = app.config["TEST_ACCT"]
                units = "feet"
            else:
                email = request.form.get("email")
                units = request.form.get("units")

            # Input validation - Thanks to emailregex.com for the regex
            regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            if not re.match(regex, email):
                e = "Please enter a valid email."
                return render_template("error.html", data=e)

            # Get user and id from MountainProject
            userid = get_userid(email)
            if userid["status"] == 1:
                e = (f"Connection error. MP Reply: {userid['code']}." +
                     " Please make sure you supplied a valid API key.")
                return render_template("error.html", data=e)
            elif userid["status"] == 2:
                e = "There is no user for that email. Please try again."
                return render_template("error.html", data=e)

            # Get ticklist from MountainProject via CSV
            csv = ticklist(userid["name"], userid["id"])
            if csv["status"] == 1:
                e = (f"Error retriving ticklist. MP Reply: {csv['code']}." +
                     " Please try again later.")
                return render_template("error.html", data=e)

            # Put user's ticklist into the database
            if not app.config["MPV_DEV"]:
                database = db_load(userid['id'], csv['data'])
                if database['status'] == 1:
                    e = f"Database error: {database['error']}"
                    return render_template('error.html', data=e)

            # Generate the stats and draw graph
            connection = db_connect()
            cursor = connection.cursor()

            height = height_climbed(cursor, userid['id'], units)
            pitches = pitches_climbed(cursor, userid['id'])

            grade_scatters = list()
            for type in get_types(cursor, userid['id']):
                reply = grade_scatter(cursor, userid['id'], type)
                if reply:
                    grade_scatters.append(reply)

            db_close(cursor, connection)

            # Show final output
            return render_template("data.html",
                                   username=userid['name'],
                                   total_height=height['total'],
                                   units=units,
                                   height=height['plot'],
                                   total_pitches=pitches['total'],
                                   pitches=pitches['plot'],
                                   scatters=grade_scatters)

        # Send them back to the index if they try to GET
        else:
            return redirect("/")

    return app

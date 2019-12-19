"""
A small webapp that functions on MountainProject.com data.

It imports data based on a user ID, then analyzes and displays it.
Code by Zach Wahrer.
"""

import re
import json
from flask import Flask, render_template, request, redirect
from helpers import get_userid, ticklist, db_load, db_connect, db_close
from graphing import height_climbed, pitches_climbed, grade_scatter, get_types


app = Flask(__name__)

with open('/etc/config.json') as config_file:
    config = json.load(config_file)

# Make sure MP API Key is set
if not config["MPV_MP_KEY"]:
    raise RuntimeError("MPV_MP_KEY not set")
# Make sure MP test acount email is set
if not config["MPV_TEST_ACCT"]:
    raise RuntimeError("MPV_TEST_ACCT email not set")


@app.route("/", methods=["GET", "POST"])
def index():
    """Show main page."""
    return render_template("index.html")


@app.route("/data", methods=["GET", "POST"])
def data():
    """Do data magic."""
    if request.method == "POST":

        # Check for test link click
        if request.form.get("test") == "yes":
            email = config["MPV_TEST_ACCT"]
            units = "feet"
        # Otherwise, import values normally
        else:
            email = request.form.get("email")
            units = request.form.get("units")

        # Input validation - Thanks to emailregex.com for the regex
        regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(regex, email):
            e = "Please enter a valid email."
            return render_template("error.html", data=e)

        # Get user and id from MP
        userid = get_userid(email)
        # Check for a successful return from MP
        if userid["status"] == 1:
            e = (f"Connection error. MP Reply: {userid['code']}." +
                 " Please make sure you supplied a valid API key.")
            return render_template("error.html", data=e)
        elif userid["status"] == 2:
            e = "There is no user connected to that email. Please try again."
            return render_template("error.html", data=e)

        # Get ticklist from MP via CSV
        csv = ticklist(userid["name"], userid["id"])
        # Check for successful data return
        if csv["status"] == 1:
            e = (f"Error retriving ticklist. MP Reply: {csv['code']}." +
                 " Please try again later.")
            return render_template("error.html", data=e)

        # Check for dev mode
        if config["MPV_DEV"] != "on":
            # Put user's ticklist into the database
            database = db_load(userid['id'], csv['data'])
            # Check for database success
            if database['status'] == 1:
                e = f"Database error: {database['error']}"
                return render_template('error.html', data=e)

        # Connect to database for graph and stats generation
        connection = db_connect()
        cursor = connection.cursor()

        # Generate the stats and draw graph
        height = height_climbed(cursor, userid['id'], units)
        pitches = pitches_climbed(cursor, userid['id'])

        grade_scatters = list()
        for type in get_types(cursor, userid['id']):
            reply = grade_scatter(cursor, userid['id'], type)
            # Check for empty returns
            if reply:
                grade_scatters.append(reply)

        # Close the connection to the database
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

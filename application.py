"""
A small webapp that functions on MountainProject.com data.

It imports data based on a user ID, then analyzes and displays it.
Code by Zach Wahrer.
"""

import os
import re
from flask import Flask, render_template, request, redirect
from helpers import get_userid, ticklist, db_load


app = Flask(__name__)

# Make sure MP API Key is set
if not os.environ.get("MPV_MP_KEY"):
    raise RuntimeError("MPV_MP_KEY not set")


@app.route("/", methods=["GET", "POST"])
def index():
    """Show main page."""
    return render_template("index.html")


@app.route("/data", methods=["GET", "POST"])
def data():
    """Do data magic."""
    if request.method == "POST":

        email = request.form.get("email")
        # Input validation - Thanks to emailregex.com for the regex
        regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(regex, email):
            e = "Please enter a valid email."
            return render_template("error.html", data=e)

        # Get user and id from MP
        userid = get_userid(request.form.get("email"))
        # Check for a successful return from MP
        if userid["status"] == 1:
            e = (f"Connection error. MP Reply: {userid['code']}." +
                 " Please make sure you supplied a valid API key.")
            return render_template("error.html", data=e)
        elif userid["status"] == 2:
            e = "There is no user connected to that email. Please try again."
            return render_template("error.html", data=e)

        # Get ticklist from MP via CSV
        csv_data = ticklist(userid["name"], userid["id"])
        # Check for successful data return
        if csv_data["status"] == 1:
            e = "Error retriving ticklist. Please try again later."
            return render_template("error.html", data=e)

        # Put user's ticklist into the database
        database = db_load(userid["id"], csv_data)
        # Check for database success
        if database["status"] == 1:
            e = f"Database error: {database['error']}"
            return render_template("error.html", data=e)

        # Show final output
        return render_template("data.html",
                               username=userid["name"], ticks=csv_data["data"])

    # Send them back to the index if they try to GET
    else:
        return redirect("/")

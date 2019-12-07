"""
A small webapp that functions on MountainProject.com data.

It imports data based on a user ID, then analyzes and displays it.
Code by Zach Wahrer.
"""

import os
import re
from flask import Flask, render_template, request, redirect
from helpers import get_userid, ticklist


app = Flask(__name__)

# Make sure MP API Key is set
if not os.environ.get("MP_KEY"):
    raise RuntimeError("MP_KEY not set")


@app.route("/", methods=["GET", "POST"])
def index():
    """Show main page."""
    return render_template("index.html")


@app.route("/data", methods=["GET", "POST"])
def data():
    """Do data magic."""
    if request.method == "POST":

        email = request.form.get("email")
        # Input validation - Thanks to emailregex.com for the regrex
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            return render_template("error.html", data="Please enter a valid email.")

        # Get user and id from MP
        userid = get_userid(request.form.get("email"))

        # Check for a successful return
        if userid[0] == 1:
            return render_template("error.html",
                                   data=f"Connection error. MP Reply: {userid[1]} Please make sure you supplied a valid API key.")
        elif userid[0] == 2:
            return render_template("error.html",
                                   data="There is no user connected to that email. Please try again.")

        # Put user's ticklist into the database
            # ticklist()

        return render_template("data.html", username=userid[1])

    else:
        return redirect("/")

"""
A webapp that functions on MountainProject.com data.

It imports data based on a user email address, then analyzes and displays it.

Code by Zach Wahrer [github.com/zachtheclimber]
and BenfromEarth [github.com/benjpalmer].
"""
from flask import Flask, redirect, render_template, request

from .config import *
from .errors.error_handlers import errors
from .forms.email_form import MPVEmailForm
from .graphing import height_climbed, pitches_climbed, grade_scatter, get_types
from .helpers.database_connection import db_close, db_connect, db_load
from .helpers.mountain_project import MountainProjectHandler


def create_app(test_config=None):
    """Create Flask app to generate web controller."""
    app = Flask(__name__)
    # Initialize error handlers.
    app.register_blueprint(errors)

    # If we are in testing env, load the test config.
    if test_config:
        app.config.from_object(test_config)
    else:
        app.config.from_object('app.config')

    @app.route("/", methods=["GET", "POST"])
    def index():
        form = MPVEmailForm()
        if form.validate_on_submit():
            return redirect("/data", code=307)
        else:
            return render_template("index.html", form=form)

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

            dev_env = app.config.get("MPV_DEV")
            # Get user and id from MP
            api = MountainProjectHandler(
                api_key=app.config.get("MP_KEY"),
                email=email,
                dev_env=dev_env
            )
            api.fetch_user()
            user_data = api.parse_user_data(dev_env=dev_env)

            # Get ticklist from MP via CSV
            api.fetch_tick_list()
            csv = api.parse_tick_list(dev_env=dev_env)
            # Lookup MP user id
            mp_user_id = user_data.get("mp_id")
            # Check for dev mode
            if not dev_env:
                # Put user's ticklist into the database
                db_load(mp_user_id, csv.get("data"), config=app.config)
            # Connect to database for graph and stats generation
            connection = db_connect(config=app.config)
            cursor = connection.cursor()
            # Generate the stats and draw graph
            height = height_climbed(cursor, mp_user_id, units)
            pitches = pitches_climbed(cursor, mp_user_id)
            grade_scatters = []
            for t in get_types(cursor, mp_user_id):
                reply = grade_scatter(cursor, mp_user_id, t)
                # Check for empty returns
                if reply:
                    grade_scatters.append(reply)

            db_close(cursor, connection)
            # Show final output
            return render_template("data.html",
                                   username=user_data.get("name"),
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

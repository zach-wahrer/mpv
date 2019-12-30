# MPV
---
MPV is a data visualizer for the rock climbing website [MountainProject.com](https://mountainproject.com). Utilizing the user's MP registered email address, MPV imports their ticked climbs, analyzes the data, and outputs a graphic visualization.

While Mountain Project has similar features available on each user's profile page, the aim for this app is to provide a more robust and analytical set of functions.

Currently, you can try the software at: [mpv.zachw.io](https://mpv.zachw.io). Check it out!

## Getting Started
---
MPV is currently in development. If you'd like to help out, feel free to jump in. :-)


### Installing
1. Make sure you have Python 3.6 installed on your machine, then run the following
shell command: `pip install -r requirements.txt`

1. On your MySQL server, create a table called `mpv`. Create a user and give them access to it. Or see next section on how
to setup database from docker.

2. Rename `config.sample.py` to `config.py`. Open it and change the listed variables. You'll need a Mountain Project API key, which you can get [here](https://www.mountainproject.com/data). The `TEST_ACCT` variable is an email address connected to a Mountain Project account. It allows users to run the app without an account (via the link on the index page) and still show data.

3. From the `setup` folder, run `python3 db_setup.py`. This will create and populate the required key tables in the MPV database.

4. To run the application on osx or Linux, set the `FLASK_APP` environment variable to `application` by running `export FLASK_APP=application`

5. Now, run `application.py` with Flask by using running the shell command `flask run`, and you should be up and running!

### Database setup with docker
1. Navigate to the root directory of the MPV project on your machine
2. run `docker-compose up`
3. To connect to the local mysql database instance with `mysql -u root -p mpv -h 127.0.0.1 -P 3306`
4. Password for development is `password`

Create your `config.json` file to look like:
```
{
    "MYSQL_USER": "root",
    "MYSQL_PASSWD": "password",
    "MYSQL_ADDRESS": "127.0.0.1",
    "MYSQL_TABLE": "mpv",
    "MP_KEY": "Your_MountainProject_API_Key_Here",
    "TEST_ACCT": "Your_MountainProject_Email_Acount_Here",
    "MPV_DEV": "on"
}
```

### Development Mode
To improve performance time and reduce traffic to the Mountain Project servers, enable development mode by setting the `MPV_DEV` variable in `config.py` to `True`. This disables loading ticks into the database via `dbload()`, sets the userid and name to dev values via `get_user_id()`, and loads `test_ticks.csv` instead of pulling one down from Mountain Project via `ticklist()`.

Note: Make sure you run the program normally at least once to build a suitable user database before enabling dev mode. You will have to rename that database `1111` in order for the program to function.  

## Built With
---
* Python3 - The controller
* Flask - The web framework
* Bokeh - The visualizer
* MySQL - The database
* Javascript - Front-end functions

## Author
---
**Zach Wahrer** - [zachtheclimber](https://github.com/zachtheclimber)

## Collaborator
---
**BenfromEarth** - [benjpalmer](https://github.com/benjpalmer)

## License
---
MPV is licensed under the GNU General Public License. Check out the [LICENSE](LICENSE) for more details.

## Acknowledgments
---
* Thanks to [emailregex.com](https://emailregex.com/) for the regex code to validate email addresses (used in both Python and Javascript).
* Another thanks goes out to Doug Neiner and Chris Coyier for the awesome [CSS background code](https://css-tricks.com/perfect-full-page-background-image/).

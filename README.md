# MPV
---
MPV is a data visualizer for the rock climbing website [MountainProject.com](https://mountainproject.com). Utilizing the user's MP registered email address, MPV imports their ticked climbs, analyzes the data, and outputs a graphic visualization.

While Mountain Project has similar features available on each user's profile page, the aim for this app is to provide a more robust and analytical set of functions.

## Getting Started
---
MPV is currently in development. If you'd like to help out, feel free to jump in. :-)

### Prerequisites
**Current requirements:**
* Python3
* Python3 Modules
  - Flask
  - Requests
  - [MySQL Connector](https://www.mysql.com/products/connector/)
  - Bokeh (v1.4.0)
* MySQL

### Installing
1. On your MySQL server, create a table called `mpv`. Create a user and give them access to it.

2. Rename `config.sample.json` to `config.json`. Open it and change the listed variables. You'll need a Mountain Project API key, which you can get [here](https://www.mountainproject.com/data). The `TEST_ACCT` variable is an email address connected to a Mountain Project account. It allows users to run the app without an account (via the link on the index page) and still show data.

3. From the `setup` folder, run `python3 db_setup.py`. This will create and populate the required key tables in the MPV database.

4. Now, run `application.py` with Flask and you should be up and running!

### Development Mode
To improve performance time and reduce traffic to the Mountain Project servers, enable development mode by setting the `MPV_DEV` variable in `config.json` to `on`. This disables loading ticks into the database via `dbload()`, sets the userid and name to dev values via `get_user_id()`, and loads `test_ticks.csv` instead of pulling one down from Mountain Project via `ticklist()`.

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

## License
---
MPV is licensed under the GNU General Public License. Check out the [LICENSE](LICENSE) for more details.

## Acknowledgments
---
* Thanks to [emailregex.com](https://emailregex.com/) for the regex code to validate email addresses (used in both Python and Javascript).
* Another thanks goes out to Doug Neiner and Chris Coyier for the awesome [CSS background code](https://css-tricks.com/perfect-full-page-background-image/).

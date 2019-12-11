# MPV
---
MPV is a data visualizer for the rock climbing website [MountainProject.com](https://mountainproject.com). Utilizing the user's MP registered email address, MPV imports their ticked climbs, analyzes the data, and outputs a graphic visualization.

While Mountain Project has a similar feature available on each user's profile page, the aim for this project is to provide a more robust and analytical set of functions.

## Getting Started
---
MPV is currently in the early stages of development. If you'd like to help out, feel free to jump in. :-)

### Prerequisites
**Current requirements:**
* Python3
* Python3 Modules
  1. Flask
  2. OS
  3. Requests
  4. Re
  5. CSV
  6. [MySQL Connector](https://www.mysql.com/products/connector/)
  7. matplotlib
* MySQL

### Installing
1. On your MySQL server, create a table called `mpv. Make sure `Collation` is set to `utf8_unicode_ci`. Create a user and give them access to it.

2. Open `helpers.py` and change the `MYSQL_USER`, `MYSQL_ADDRESS` variables to your new username and server address. Do the same for `setup/db_setup.py`.

3. Export your password to the `MPV_MYSQL_PASSWD` environment variable.

4. From the `setup` folder, run `python3 db_setup.py`. This will create and populate the required key tables in the MPV database.

5. Next, configure the `MPV_MP_KEY` environment variable as a Mountain Project API key. You can get one [here](https://www.mountainproject.com/data).

6. Now, run `application.py` with Flask and you should be set!

### Development Mode
To improve performance time and reduce traffic to the Mountain Project servers, enable development mode by setting the `MPV_DEV` environment variable to `on`. This disables loading ticks into the database via `dbload()`, sets the userid and name to dev values via `get_user_id()`, and loads `test_ticks.csv` instead of pulling one down from Mountain Project via `ticklist()`.

Note: Make sure you run the program normally at least once to build a suitable user database before enabling dev mode. You will have to rename that database `1111` in order for the program to function.  

## Built With
---
* Python3 - The controller
* Flask - The web framework
* MySQL - The database
* Javascript - Front-end functions

## Authors
---
**Zach Wahrer** - [zachtheclimber](https://github.com/zachtheclimber)

## License
---
MPV is licensed under the GNU General Public License. Check out the [LICENSE](LICENSE) for more details.

## Acknowledgments
---
* Thanks to [emailregex.com](https://emailregex.com/) for the regex code to validate email addresses (used in both Python and Javascript).

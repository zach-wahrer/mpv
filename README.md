# MPV
---
MPV is a data visualizer for the rock climbing website [MountainProject.com](https://mountainproject.com). Utilizing the user's MP registered email address, MPV imports their ticked climbs, analyzes the data, and outputs a graphic visualization.

While Mountain Project has similar features available on each user's profile page, the aim for this app is to provide a more robust and analytical set of functions.

Currently, you can try the software at: [mpv.zachw.io](https://mpv.zachw.io). Check it out!

## Getting Started
---
MPV is currently in development. If you'd like to help out, feel free to jump in. :-)


### Installing With Docker
1. In the `app` directory, rename `config.sample.py` to `config.py`. Open it and change the listed variables (minus anything to do with MySQL). See the **Configuration** section below for additional help.

2. From the project's root directory, execute `docker build -t mpv .` This will build a Docker image of MPV, using your supplied configuration.

3. Still from the project's root directory, run `docker-compose up -d`. This will start two Docker containers, one for MPV and another for the required MySQL database.

4. Use Docker to log in to the MPV container: `docker exec -it `container-id` bash`, substituting `container-id` for the MPV instance. `docker ps` will show it to you.

5. Once you have a terminal inside the MPV container, run `python3 -m app.setup.db_setup`. This will load the required tables into the MySQL database, and only needs to be done once.

6. Now, you should be able to open `127.0.0.1:5000` in your web browser and see a running MPV!


### Manual Install (With Optional Docker MySQL Container)
1. Make sure you have Python 3.6 installed on your machine, then run the following
shell command: `pip install -r requirements.txt`

2. On your MySQL server, create a table called `mpv`. Create a user and give them access to it. Or see next section on how
to setup database from docker.

3. In the `app` directory, rename `config.sample.py` to `config.py`. Open it and change the listed variables. See the **Configuration** section below for help.

4. From your root project directory, run `python -m app.setup.db_setup`. This will create and populate the required key tables in the MPV database.

5. Now, start the application by using the shell command `flask run` in the root project directory, and you should be up and running!

### Database Setup With Docker
1. Navigate to the root directory of the MPV project on your machine
2. run `docker-compose up`
3. To connect to the local mysql database instance with `mysql -u root -p mpv -h 127.0.0.1 -P 3306`
4. Password for development is `password`

### Configuration
This application looks for a `config.py` file located in the `app` directory of your project. With that in mind,
structure your file to look like the example below, changing any values as necessary.
```
SECRET_KEY = "super-secret-key"
WTF_CSRF_SECRET_KEY = "different-super-secret-key"
MYSQL_USER = "root"
MYSQL_PASSWD = "password"
MYSQL_ADDRESS = "127.0.0.1"
MYSQL_TABLE = "mpv"
MP_KEY = "Your_MountainProject_API_Key_Here"
TEST_ACCT = "Your_MountainProject_Email_Acount_Here"
MPV_DEV = True
```
`SECRET_KEY` is used by Flask and extensions to "keep data safe". Set it to a random value. In the same vein, `WTF_CSRF_SECRET_KEY` is used by the `Flask-WTF` module. Assign it a different random value.

`MP_KEY` is a Mountain Project API key, which you can get [here](https://www.mountainproject.com/data). The `TEST_ACCT` variable is an email address connected to a Mountain Project account. It allows users to run the app without an account (via the link on the index page) and still show data. For more on `MPV_DEV`, see **Development Mode** below.

### Testing

To add tests please add them in under the `app/tests` directory.
Testing is done via Pytest. For documentation please visit https://docs.pytest.org/en/latest/index.html
To run tests simply run the following shell command: `pytest`

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
* Thanks to Doug Neiner and Chris Coyier for the awesome [CSS background code](https://css-tricks.com/perfect-full-page-background-image/).

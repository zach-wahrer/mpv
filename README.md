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
* MySQL (*Coming soon*)

### Installing
Running application.py with Flask will get you up and running. Configuring the `MP_KEY` environment variable as a MP API key is required. Get one: [https://www.mountainproject.com/data].

## Built With
---
* Python3 - The controller
* Flask - The web framework
* MySQL - The database (*Coming soon*)
* Javascript - Front-end functions

## Authors
---
**Zach Wahrer** - [zachtheclimber](https://github.com/zachtheclimber)

## License
---
MPV is licensed under the GNU General Public License. Check out the [LICENSE](LICENSE) for more details.

## Acknowledgments
---
* Thanks to [emailregex.com](https://emailregex.com/) for the regrex code to validate email addresses (used in both Python and Javascript).

import csv
from typing import Dict, Union

import requests
from requests import ConnectionError, ConnectTimeout, HTTPError, ReadTimeout, Timeout


_DEV_USER_DATA = {"status": 0, "name": "Dev", "id": 1111}
_DEV_TEST_TICKS = "test_ticks.csv"


class MountainProjectParser:
    """Responsible for the processing and temporary storage of Mountain Project API data. """
    api_data = {}

    def __init__(self):
        self._mp_id = None
        self._mp_username = None

    def parse_user_data(self, dev_env: bool = False) -> Dict:
        """Parse the request into JSON data and return username and mountain project ID."""
        try:
            if dev_env:
                return _DEV_USER_DATA
            else:
                user_data = self.api_data.get('user_data').json()
                self._mp_id = user_data.get("id")
                self._mp_username = user_data.get("name")
                return {"status": 0, "name": self._mp_username, "mp_id": self._mp_id}
        except ValueError:
            # In case the JSON decoding fails, r.json() raises a ValueError
            return {"status": 2}

    def parse_tick_list(self, dev_env: bool = False) -> Dict:
        """Parse the request data into a CSV and clean."""
        try:
            if dev_env:
                with open(_DEV_TEST_TICKS) as ticklist:
                    ticklist = list(csv.reader(ticklist, delimiter=','))
            else:
                tick_list = self.api_data.get("tick_list").content.decode("utf-8")
                ticklist = list(csv.reader(tick_list.splitlines(), delimiter=','))
            # Delete in reverse order to make field posistions simpler
            remove = [12, 8, 7, 6, 4, 3, 2]
            for row in ticklist:
                for i in remove:
                    del row[i]
            # Remove the CSV header
            del ticklist[0]
            return {"status": 0, "data": ticklist}
        except (AttributeError, IndexError, UnicodeDecodeError) as e:
            return {"status": 1, "code": e}


class MountainProjectHandler(MountainProjectParser):
    """Responsible for interacting with the Mountain Project api."""
    def __init__(self, api_key: str = None, email: str = None, dev_env: bool = False):
        super().__init__()
        self._api_key = api_key
        self._email = email
        self.base_url = "https://www.mountainproject.com"
        self.dev_env = dev_env

    def _mp_generic_request(self, obj_key: str,  url: str, params: Dict = None, timeout: int = 30):
        try:
            r = requests.get(url, params, timeout=timeout)
            # add response to super class dictionary for processing.
            self.api_data.update({obj_key: r})
            return r
        except (ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError):
            # TODO We should think about error handling a little bit more
            return {"status": 1, "code": r.status_code}

    def fetch_user(self) -> Union["requests", Dict]:
        """Executes request to /data/get-user endpoint."""
        if self.dev_env:
            return _DEV_USER_DATA
        params = {"key": self._api_key, "email": self._email}
        return self._mp_generic_request(
            url=f"{self.base_url}/data/get-user",
            params=params,
            obj_key='user_data'
        )

    def fetch_tick_list(self) -> Union["requests", None]:
        """Executes request to /user/<mp_id>/<mp_username>/tick-export."""
        if self.dev_env:
            return
        return self._mp_generic_request(
            url=f"{self.base_url}/user/{self._mp_id}/{self._mp_username}/tick-export",
            obj_key='tick_list'
        )

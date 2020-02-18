from ..errors.exeptions import *
import io
import pandas as pd
from pandas.errors import EmptyDataError, ParserError
import requests
from requests import ConnectionError, ConnectTimeout, HTTPError, ReadTimeout, Timeout
from typing import Dict, Optional, Union


_DEV_USER_DATA = {"status": 0, "name": "Dev", "mp_id": 1111}
_DEV_TEST_TICKS = "test_ticks.csv"


class MountainProjectParser:
    """Responsible for the processing and temporary storage of Mountain Project API data. """
    api_data = {}

    def __init__(self):
        self._mp_id = None
        self._mp_username = None

    def parse_user_data(self, dev_env: bool = False) -> Dict:
        """Parse the request into JSON data and return username and mountain project ID."""
        if dev_env:
            return _DEV_USER_DATA
        else:
            try:
                user_data = self.api_data.get('user_data').json()
            except ValueError:
                # In case the JSON decoding fails, r.json() raises a ValueError.
                raise MPAPIException

            self._mp_id = user_data.get("id")
            self._mp_username = user_data.get("name")
            return {"status": 0, "name": self._mp_username, "mp_id": self._mp_id}

    def parse_tick_list(self, dev_env: bool = False) -> Dict:
        """Parse the request data into a Pandas dataframe to clean."""
        columns = ["Date", "Route", "Pitches", "Style",
                   "Lead Style", "Route Type", "Length", "Rating Code"]
        if dev_env:
            with open(_DEV_TEST_TICKS) as tick_list_file:
                df = pd.read_csv(tick_list_file, usecols=columns,
                                 na_filter=False)
        else:
            try:
                tick_list = self.api_data.get("tick_list").content.decode("utf-8")
                df = pd.read_csv(io.StringIO(tick_list),
                                 usecols=columns, na_filter=False)
            except (AttributeError, UnicodeDecodeError, EmptyDataError, ParserError) as e:
                raise MPAPIException

        return {"status": 0, "data": df.values.tolist()}


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
            mp_request = requests.get(url, params, timeout=timeout, stream=True)
        except (ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError):
            raise RequestException

        # add response to super class dictionary for processing.
        self.api_data.update({obj_key: mp_request})
        return mp_request

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

    def fetch_tick_list(self) -> Optional["requests"]:
        """Executes request to /user/<mp_id>/<mp_username>/tick-export."""
        if self.dev_env:
            return

        return self._mp_generic_request(
            url=f"{self.base_url}/user/{self._mp_id}/{self._mp_username}/tick-export",
            obj_key='tick_list'
        )

import csv
from typing import Dict

from requests import ConnectionError, ConnectTimeout, get, HTTPError, ReadTimeout, Timeout


class MountainProjectParser:
    api_data = {}

    def __init__(self):
        self._mp_id = None
        self._mp_username = None

    def parse_user_data(self) -> Dict:
        try:
            # In case the JSON decoding fails, r.json() raises a ValueError
            user_data = self.api_data.get('user_data').json()
            self._mp_id = user_data.get("id")
            self._mp_username = user_data.get("name")
            return {"status": 0, "name": self._mp_username, "mp_id": self._mp_id}
        except ValueError:
            return {"status": 2}

    def parse_tick_list(self):
        try:
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
        except (IndexError, AttributeError) as e:
            return {"status": 1, "code": e}


class MountainProjectHandler(MountainProjectParser):
    """Responsible for interacting with the Mountain Project api."""
    def __init__(self, api_key: str = None, email: str = None):
        super().__init__()
        self._api_key = api_key
        self._email = email
        self.base_url = "https://www.mountainproject.com"

    def _mp_generic_request(self, obj_key: str,  url: str, params: dict = None, timeout: int = 30):
        try:
            r = get(url, params, timeout=timeout)
            r.raise_for_status()
            # add response to super class dictionary for processing.
            self.api_data.update({obj_key: r})
            return r
        except (ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError):
            return {"status": 1, "code": r.status_code}

    def fetch_user(self):
        # build the query parameters
        params = {"key": self._api_key, "email": self._email}
        # return the data
        return self._mp_generic_request(url=f"{self.base_url}/data/get-user", params=params, obj_key='user_data')

    def lookup_ticklist(self):
        return self._mp_generic_request(url=f"{self.base_url}/user/{self._mp_id}/{self._mp_username}/tick-export", obj_key='tick_list')

from requests import ConnectionError, ConnectTimeout, get, HTTPError, ReadTimeout, Timeout


class MountainProjectApi:
    """Responsible for interacting with the Mountain Project api."""
    def __init__(self):
        self.base_url = "https://www.mountainproject.com"
        self.data = None

    @staticmethod
    def _mp_generic_request(url: str, params: dict = None, timeout: int = 30):
        try:
            r = get(url, params, timeout=timeout)
            r.raise_for_status()
            return r
        except (ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError):
            return {"status": 1, "code": r.status_code}

    def lookup_user(self, email: str, api_key: str):
        # build the query parameters
        params = {"key": api_key, "email": email}
        # return the data
        return self._mp_generic_request(url=f"{self.base_url}/data/get-user", params=params).json()

    def lookup_ticklist(self, username, mp_id):
        return self._mp_generic_request(url=f"{self.base_url}/user/{mp_id}/{username}/tick-export")

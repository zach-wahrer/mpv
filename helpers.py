import os
import requests


def get_userid(email):
    """
    Get username/id using email via MountainProject.com API.

    (https://www.mountainproject.com/data)
    """
    # Get API Key
    api_key = os.environ.get("MP_KEY")

    # Get info from MountainProject
    try:
        reply = requests.get(
            f"https://www.mountainproject.com/data/get-user?email={email}&key={api_key}")
        reply.raise_for_status()
    except requests.RequestException:
        return [1, reply.status_code]

    # Parse the reply
    try:
        data = reply.json()
    except (KeyError, TypeError, ValueError):
        return [2]

    # Format the return
    return [3, data['name'], data['id']]


def ticklist():
    """
    Download a CSV file of all users ticks from MP.

    i.e. https://www.mountainproject.com/user/{id}/{username}/tick-export
    """
    # TODO #
    return False

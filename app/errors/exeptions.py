class MPAPIException(Exception):
    status_code = 403
    msg = "An error occurred fetching data from the Mountain Project API. " \
        "Make sure you're using a valid, MP registered email address, " \
          "or try your request later."


class DatabaseException(Exception):
    status_code = 503
    msg = "Something went wrong on our end. Please try again later."


class RequestException(Exception):
    status_code = 400
    msg = "Something went wrong on our end. Please try again later."

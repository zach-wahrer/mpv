class MPAPIException(Exception):
    status_code = 403
    msg = "An error occurred fetching data the Mountain Project API. Make sure are using your correct email address, " \
          "or try your request later."


class DatabaseException(Exception):
    status_code = 503
    msg = "Something went wrong on our end. We are working on a fix, please try again later."


class RequestException(Exception):
    status_code = 400
    msg = "Something went wrong on our end. We are working on a fix, please try again later."

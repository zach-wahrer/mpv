class APIKeyInvalidException(Exception):
    status_code = 403
    msg = "Please make sure you supplied a valid API key."


class DatabaseConnectionException(Exception):
    status_code = 503
    msg = "Database is messed up"

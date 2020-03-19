from werkzeug.exceptions import BadRequest, Forbidden, ServiceUnavailable, UnprocessableEntity


class MPAPIException(Forbidden):
    status_code = 403
    msg = "An error occurred fetching data from the Mountain Project API. " \
        "Make sure you are using a valid, MP registered email address, " \
          "or try your request later."


class DatabaseException(ServiceUnavailable):
    status_code = ServiceUnavailable.code
    msg = "Something went wrong on our end. Please try again later."


class RequestException(BadRequest):
    status_code = BadRequest.code
    msg = "Something went wrong on our end. Please try again later."


class UnprocessableEntityException(UnprocessableEntity):
    status_code = UnprocessableEntity.code
    msg = "An error occurred. Please make sure you provided a registered MP email address."

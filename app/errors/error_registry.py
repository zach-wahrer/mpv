from enum import Enum

from .exeptions import *


class ExceptionRegistry(Enum):
    MPAPIException = MPAPIException()
    DatabaseException = DatabaseException()
    RequestException = RequestException()
    UnprocessableEntityException = UnprocessableEntityException()

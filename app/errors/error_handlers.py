import logging

from flask import Blueprint, render_template
from werkzeug.exceptions import NotFound

from .exeptions import *


errors = Blueprint('errors', __name__)


@errors.app_errorhandler(RequestException)
def handle_400(error: RequestException):
    logging.exception(error)
    return render_template("error.html", data=RequestException.msg), 400


@errors.app_errorhandler(MPAPIException)
def handle_403(error: MPAPIException):
    logging.exception(error)
    return render_template("error.html", data=MPAPIException.msg), 403


@errors.app_errorhandler(404)
def handle_404(error: NotFound):
    logging.exception(error)
    return render_template("error.html", data=error), 404


@errors.app_errorhandler(UnprocessableEntityException)
def handle_422(error: UnprocessableEntityException):
    logging.exception(error)
    return render_template("error.html", data=UnprocessableEntityException.msg), 422


@errors.app_errorhandler(DatabaseException)
def handle_503(error: DatabaseException):
    logging.exception(error)
    return render_template("error.html", data=DatabaseException.msg), 503

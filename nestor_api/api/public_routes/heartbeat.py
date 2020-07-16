"""Define the heartbeat route."""
from http import HTTPStatus

from flask import Blueprint

blueprint = Blueprint("heartbeat", __name__)


@blueprint.route("/heartbeat")
def heartbeat():
    """A heartbeat route for monitoring purpose (no auth!)."""
    return "", HTTPStatus.NO_CONTENT

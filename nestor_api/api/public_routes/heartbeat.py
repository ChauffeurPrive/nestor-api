"""Define the heartbeat route."""
from flask import Blueprint

blueprint = Blueprint("heartbeat", __name__)


@blueprint.route("/heartbeat")
def heartbeat():
    """A heartbeat route for monitoring purpose (no auth!)."""
    return "", 204

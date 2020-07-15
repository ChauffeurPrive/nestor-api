"""Register all routes under the /api prefixes. The route /heartbeat is not included."""
from flask import Blueprint

from .api_routes import builds


def create_api() -> Blueprint:
    """Return the collection of routes and other app-related functions."""
    api = Blueprint("api", __name__, url_prefix="/api")

    builds.register_routes(api=api)

    return api

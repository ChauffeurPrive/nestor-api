"""Register all routes under the /api/v1 prefixes."""
from flask import Blueprint

from . import builds


def create_api() -> Blueprint:
    """Return the collection of routes and other app-related functions."""
    api = Blueprint("api", __name__, url_prefix="/api/v1")

    builds.register_routes(api=api)

    return api

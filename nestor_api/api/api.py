"""
    Register all routes for each apis under the /api prefixes.
    The route /heartbeat is not included.
"""

from nestor_api.api.api_routes.v1 import create_api_v1


def get_apis() -> list:
    """Return the list of apis to register."""

    return [
        create_api_v1(),
    ]

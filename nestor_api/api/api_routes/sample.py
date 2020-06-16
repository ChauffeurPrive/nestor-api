"""Define the sample route."""
from flask import Blueprint, Response, jsonify


def register_routes(api: Blueprint) -> None:
    """Register the /sample route."""

    @api.route("/sample", methods=["GET"])
    def sample() -> Response:  # pylint: disable=unused-variable
        """Return a hello world."""
        return jsonify({"sample": "Hello, world!"})

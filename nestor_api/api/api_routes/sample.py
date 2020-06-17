"""Define the sample route."""
from flask import Blueprint, Response, jsonify


def register_routes(api: Blueprint) -> None:
    """Register the /sample routes."""

    @api.route("/sample", methods=["GET"])
    def _sample() -> Response:
        """Return a hello world."""
        return jsonify({"sample": "Hello, world!"})

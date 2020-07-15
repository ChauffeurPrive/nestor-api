"""Defines the builds route."""
from flask import Blueprint, Response

from .build_app import build_app


def register_routes(api: Blueprint) -> None:
    """Register the `/builds` routes."""

    @api.route("/builds/<app_name>", methods=["POST"])
    def _build_app(app_name: str) -> Response:
        return build_app(app_name)

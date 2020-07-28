"""Define the workflow controllers."""

from flask import Blueprint

from nestor_api.api.api_routes.workflow.workflow import init_workflow


def register_routes(api: Blueprint) -> None:
    """Register the workflow routes."""

    @api.route("/workflow/init/<organization>/<app>", methods=["POST"])
    def _init_workflow(organization, app):
        return init_workflow(organization, app)

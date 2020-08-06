"""Define the workflow controllers."""

from flask import Blueprint

from nestor_api.api.api_routes.workflow.init import init_workflow
from nestor_api.api.api_routes.workflow.advance import advance_workflow


def register_routes(api: Blueprint) -> None:
    """Register the workflow routes."""

    @api.route("/workflow/init/<organization>/<app>", methods=["POST"])
    def _init_workflow(organization, app):
        return init_workflow(organization, app)

    @api.route("/workflow/progress/<current_step>", methods=["POST"])
    def _advance_workflow(current_step):
        return advance_workflow(current_step)

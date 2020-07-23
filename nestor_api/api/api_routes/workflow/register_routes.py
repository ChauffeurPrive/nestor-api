"""Define the workflow controllers."""

from flask import Blueprint, request

from nestor_api.api.api_routes.workflow.workflow import advance_workflow, init_workflow


def register_routes(api: Blueprint) -> None:
    """Register the workflow routes."""

    @api.route("/workflow/init/<organization>/<app>", methods=["POST"])
    def _init_workflow(organization, app):
        return init_workflow(organization, app)

    @api.route("/progress/<current_step>", methods=["POST"])
    def _advance_workflow(current_step):
        return advance_workflow(current_step, sync=False)

    @api.route("/progress_sync/<current_step>", methods=["POST"])
    def _advance_workflow(current_step):
        return advance_workflow(current_step, request.form["tags"], sync=True)

"""Workflow library errors."""


class WorkflowError(Exception):
    """A generic error happened in the workflow."""


class StepNotExistingInWorkflowError(WorkflowError):
    """The step does not exist in the workflow."""


class AppListingError(WorkflowError):
    """An error happened listing project applications."""


class WorkflowAdvanceError(WorkflowError):
    """An error happened advancing an application."""

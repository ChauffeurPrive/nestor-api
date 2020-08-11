"""Workflow library typings."""

from collections import namedtuple
from enum import Enum
from typing import Dict, List, TypedDict


class WorkflowInitStatus(Enum):
    """Enum for workflow initialization status."""

    SUCCESS = "SUCCESS"
    FAIL = "FAIL"


class WorkflowAdvanceStatus(Enum):
    """Enum for workflow advance status."""

    SUCCESS = "SUCCESS"
    FAIL = "FAIL"


CreationStatus = namedtuple("CreationStatus", ["is_modified", "is_created"])
ProtectionStatus = namedtuple("ProtectionStatus", ["is_modified", "is_protected"])


class BranchReport(TypedDict, total=False):
    """Branch report dictionary."""

    created: CreationStatus
    protected: ProtectionStatus


Report = Dict[str, BranchReport]


class AdvanceWorkflowAppReport(TypedDict):
    """Advance workflow report dictionary."""

    name: str
    tag: str
    step: str
    processes: List
    cron_jobs: List

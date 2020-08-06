"""Workflow library typings."""

from collections import namedtuple
from enum import Enum
from typing import Dict, TypedDict


class WorkflowInitStatus(Enum):
    """Enum for workflow initialization status."""

    SUCCESS = "SUCCESS"
    FAIL = "FAIL"


CreationStatus = namedtuple("CreationStatus", ["is_modified", "is_created"])
ProtectionStatus = namedtuple("ProtectionStatus", ["is_modified", "is_protected"])


class BranchReport(TypedDict, total=False):
    """Branch report dictionary"""

    created: CreationStatus
    protected: ProtectionStatus


Report = Dict[str, BranchReport]

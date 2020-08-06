"""Kubernetes resource types"""

from enum import Enum


class K8sResourceType(Enum):
    """An enum representing the different resources kinds"""

    DEPLOYMENTS = "deployments"
    CRONJOBS = "cronjobs"

    def __str__(self):
        return str(self.value)

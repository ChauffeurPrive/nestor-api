"""Kubernetes resource types"""

from enum import Enum


class K8sResourceKind(Enum):
    """An enum representing the different resources kinds"""

    DEPLOYMENT = "Deployment"
    CRONJOB = "CronJob"

    def __str__(self):
        return str(self.value)

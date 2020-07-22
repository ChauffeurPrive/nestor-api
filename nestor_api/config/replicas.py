"""Replicas default configuration"""

import os


class ReplicasDefaultConfiguration:
    """Replicas default configuration"""

    @staticmethod
    def get_default_min_replicas():
        """Returns the replicas default min"""
        return int(os.getenv("NESTOR_REPLICAS_DEFAULT_MIN", "1"))

    @staticmethod
    def get_default_max_replicas():
        """Returns the replicas default max"""
        return int(os.getenv("NESTOR_REPLICAS_DEFAULT_MAX", "10"))

    @staticmethod
    def get_default_target_cpu_utilization_percentage():
        """Returns the default target cpu utilization percentage that will trigger an autoscaling"""
        return int(os.getenv("NESTOR_REPLICAS_DEFAULT_TARGET_CPU_USAGE", "75"))

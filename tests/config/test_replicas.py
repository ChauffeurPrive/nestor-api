import os
from unittest import TestCase
from unittest.mock import patch

from nestor_api.config.replicas import ReplicasDefaultConfiguration


class TestReplicasConfig(TestCase):
    @patch.dict(os.environ, {"NESTOR_REPLICAS_DEFAULT_MIN": "2"})
    def test_get_default_min_replicas_configured(self):
        self.assertEqual(ReplicasDefaultConfiguration.get_default_min_replicas(), 2)

    def test_get_default_min_replicas_default(self):
        self.assertEqual(ReplicasDefaultConfiguration.get_default_min_replicas(), 1)

    @patch.dict(os.environ, {"NESTOR_REPLICAS_DEFAULT_MAX": "5"})
    def test_get_default_max_replicas_configured(self):
        self.assertEqual(ReplicasDefaultConfiguration.get_default_max_replicas(), 5)

    def test_get_default_max_replicas_default(self):
        self.assertEqual(ReplicasDefaultConfiguration.get_default_max_replicas(), 10)

    @patch.dict(os.environ, {"NESTOR_REPLICAS_DEFAULT_TARGET_CPU_USAGE": "80"})
    def test_get_default_target_cpu_utilization_percentage_configured(self):
        self.assertEqual(
            ReplicasDefaultConfiguration.get_default_target_cpu_utilization_percentage(), 80
        )

    def test_get_default_target_cpu_utilization_percentage_default(self):
        self.assertEqual(
            ReplicasDefaultConfiguration.get_default_target_cpu_utilization_percentage(), 75
        )

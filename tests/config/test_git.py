import os
from unittest import TestCase
from unittest.mock import patch

from nestor_api.config.git import GitConfiguration


# pylint: disable=too-few-public-methods
class TestGitConfig(TestCase):
    @patch.dict(os.environ, {"NESTOR_GIT_PROVIDER_TOKEN": "secret"})
    def test_get_git_provider_token_configured(self):
        self.assertEqual(GitConfiguration.get_git_provider_token(), "secret")

    def test_get_git_provider_token_default(self):
        self.assertIsNone(GitConfiguration.get_git_provider_token())

    @patch.dict(os.environ, {"NESTOR_GIT_MASTER_TAG": "production"})
    def test_get_master_tag_configured(self):
        self.assertEqual(GitConfiguration.get_master_tag(), "production")

    def test_get_master_tag_default(self):
        self.assertEqual(GitConfiguration.get_master_tag(), "master")

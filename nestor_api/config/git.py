"""Git configuration"""

import os


# pylint: disable=too-few-public-methods
class GitConfiguration:
    """Git configuration"""

    @staticmethod
    def get_git_provider_token():
        """Returns the git provider token use to access provider APIs"""
        return os.getenv("NESTOR_GIT_PROVIDER_TOKEN", None)

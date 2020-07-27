"""Git configuration"""

import os


class GitConfiguration:
    """Git configuration"""

    @staticmethod
    def get_git_provider_token():
        """Returns the git provider token use to access provider APIs"""
        return os.getenv("NESTOR_GIT_PROVIDER_TOKEN", None)

    @staticmethod
    def get_master_tag():
        """Returns the master tag"""
        return os.getenv("NESTOR_GIT_MASTER_TAG", "master")

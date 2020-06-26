# pylint: disable=missing-function-docstring disable=missing-module-docstring

import nestor_api.lib.config as config


def test_get_app_config():
    configuration = config.get_app_config("my-app")
    assert configuration == dict({"app_name": "my-app"})

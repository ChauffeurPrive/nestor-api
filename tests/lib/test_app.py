import nestor_api.lib.app as app


def test_get_version():
    version = app.get_version()
    assert version == "0.0.0"

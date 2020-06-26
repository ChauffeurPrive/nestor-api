"""Configuration and fixtures for pytest."""

import pytest


@pytest.fixture
def config(monkeypatch):
    """Define the project configuration for tests"""

    monkeypatch.setenv("NESTOR_CONFIG_PATH", "/fixtures-nestor-config")
    monkeypatch.setenv("NESTOR_PRISTINE_PATH", "/fixtures-nestor-pristine")
    monkeypatch.setenv("NESTOR_WORK_PATH", "/fixtures-nestor-work")

"""Setup script for nestor-api."""

from setuptools import find_packages, setup

import nestor_api

setup(
    name=nestor_api.__name__,
    version=nestor_api.__version__,
    url="https://github.com/ChauffeurPrive/nestor-api",
    python_requires=">=3.8",
    author_email="tech-admin@kapten.com",
    description="API to manages kubernetes deployments",
    packages=find_packages(),
    install_requires=[],
)

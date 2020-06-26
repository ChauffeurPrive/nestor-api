# nestor-api · [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ChauffeurPrive/nestor-api/blob/master/LICENSE) [![Workflow](https://github.com/ChauffeurPrive/nestor-api/workflows/ci/badge.svg?branch=master)](https://github.com/ChauffeurPrive/nestor-api/actions?query=workflow%3Aci+branch%3Amaster) [![codecov](https://codecov.io/gh/ChauffeurPrive/nestor-api/branch/master/graph/badge.svg)](https://codecov.io/gh/ChauffeurPrive/nestor-api)

Nestor-api is an API used to manage deployment of applications Kubernetes. It can be used with [nestor-cli](https://github.com/ChauffeurPrive/nestor-cli), a CLI tool consuming nestor-api.

## Installing

Python 3.7 or above.

Dependencies are managed by [Pipenv](https://github.com/pypa/pipenv).

```bash
pipenv sync # Add --dev to also install dev dependencies
```

## Running the tests 

```bash
pipenv run make pytest
```

## Configuration

> [Source](./nestor_api/config/config.py)

|                              Key | Default                | Unit | Comment                       |
| -------------------------------: | ---------------------- | ---- | ----------------------------- |
|             `NESTOR_CONFIG_PATH` |                        |      | Configuration path            |
|      `NESTOR_CONFIG_APPS_FOLDER` | `apps`                 |      | The application config folder |
| `NESTOR_CONFIG_PROJECT_FILENAME` | `project.yaml`         |      | The project config file       |
|           `NESTOR_PRISTINE_PATH` | `/tmp/nestor/pristine` |      | Pristine path                 |
|               `NESTOR_WORK_PATH` | `/tmp/nestor/work`     |      | Work path                     |

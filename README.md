# nestor-api · [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ChauffeurPrive/nestor-api/blob/master/LICENSE) [![Workflow](https://github.com/ChauffeurPrive/nestor-api/workflows/ci/badge.svg?branch=master)](https://github.com/ChauffeurPrive/nestor-api/actions?query=workflow%3Aci+branch%3Amaster) [![codecov](https://codecov.io/gh/ChauffeurPrive/nestor-api/branch/master/graph/badge.svg)](https://codecov.io/gh/ChauffeurPrive/nestor-api)

Nestor-api is an API used to manage deployment of applications Kubernetes. It can be used with [nestor-cli](https://github.com/ChauffeurPrive/nestor-cli), a CLI tool consuming nestor-api.

## Installing

Python 3.7 or above.

Dependencies are managed by [Pipenv](https://github.com/pypa/pipenv).

```bash
pipenv sync # Add --dev to also install dev dependencies
```

## Configuration

> [Source](./nestor_api/config/config.py)

|                                        Key | Default                | Unit       | Comment                                                     |
| -----------------------------------------: | ---------------------- | ---------- | ----------------------------------------------------------- |
|                       `NESTOR_CONFIG_PATH` |                        |            | Configuration path                                          |
|                `NESTOR_CONFIG_APPS_FOLDER` | `apps`                 |            | The application config folder                               |
|           `NESTOR_CONFIG_PROJECT_FILENAME` | `project.yaml`         |            | The project config file                                     |
|             `NESTOR_CONFIG_DEFAULT_BRANCH` | `staging`              |            | The branch to use by default when reading the configuration |
|                     `NESTOR_PRISTINE_PATH` | `/tmp/nestor/pristine` |            | Pristine path                                               |
|                         `NESTOR_WORK_PATH` | `/tmp/nestor/work`     |            | Work path                                                   |
|              `NESTOR_PROBES_DEFAULT_DELAY` | `30`                   | `seconds`  | Default delay for probes if not configured                  |
|             `NESTOR_PROBES_DEFAULT_PERIOD` | `10`                   | `seconds`  | Default period for probes if not configured                 |
|            `NESTOR_PROBES_DEFAULT_TIMEOUT` | `1`                    | `seconds`  | Default timeout for probes if not configured                |
|              `NESTOR_REPLICAS_DEFAULT_MIN` | `1`                    | `replicas` | Default minimum number of replicas                          |
|              `NESTOR_REPLICAS_DEFAULT_MAX` | `10`                   | `replicas` | Default maximum number of replicas                          |
| `NESTOR_REPLICAS_DEFAULT_TARGET_CPU_USAGE` | `75`                   | `%`        | Default target cpu usage that will trigger an autoscaling   |
|                    `NESTOR_K8S_HTTP_PROXY` |                        |            | The kubernetes HTTP_PROXY                                   |
|                     `NESTOR_K8S_HTTP_PORT` | `8080`                 |            | The port on which the k8s services will be exposed          |
|               `NESTOR_K8S_TEMPLATE_FOLDER` | `templates`            |            | The subfolder in which the k8s templates are stored         |

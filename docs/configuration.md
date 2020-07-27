# Nestor configuration

## Context

Nestor configuration contains configuration of how apps are configured and deployed.

## How to use it

Nestor configuration's should be in a dedicated repository, so that you can keep track of changes.
The repository should have one branch for each step of the workflow defined in the `project.yaml`.

## Details

### Project

The `project.yaml` contains global configuration.
You can find default values in this file but also global configuration (e.g. docker registry, workflow's steps).

### Application

Applications' configurations can be found under `apps` folder.
This configuration will be merged with the `project.yaml` configuration.
If values are defined in both project configuration and application configuration, application will overwrite the project configuration.

There are 2 sections of `variables` in the application configuration:

- `app`: these variables are application levels configurations (e.g. number of retries).
- `ope`: these variables are configuration that are external components/services configurations (e.g. database connections).

Both will end up being environment variables for the application when deployed.

### Configuration

To have more details, check the [validator documentation](../validator/docs/schemas.md).

# API

## Builds

### POST `/api/builds/:app`

<a name="api-build-api"></a>

Builds the docker image of an application from the first step defined in the workflow with a unique
tag and uploads it to the configured Docker registry.

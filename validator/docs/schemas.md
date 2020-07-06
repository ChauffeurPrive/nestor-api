# Configuration Validator

This module contains the logic needed to validate deployment files with a defined schema by Nestor.

The deployment files define applications or projects.

## Application Configuration

In each file you will define the application that you want to deploy, there are few fields which are required to setup a new application.

This is a basic configuration application with the minimum required fields.

```yaml
app: my-application   # Application's name
is_enabled: false     # Is application deployment enabled
git: git@microservice_repo # Git repository URL
variables:            # Environment variables
  app:
    APP_VAR1: application_variable_1
  ope:
    OPE_VAR1: ope_variable_1
```

To customize your application deployment, there are other sections supported. Check the following sections.

### Processes

Define processes of a project. A project can contain multiple processes such as workers, web processes and more.
The structure to define a process is the following:

```yaml
processes:
  - name: process-name  # Process name, STRING - Required
    is_cronjob: false   # Defining a simple process, BOOLEAN - Required
    start_command: npm start  # Executed command when the pod is started. STRING - Required
  - name: cronjob-name  # Process name - Required
    is_cronjob: true    # Defining a scheduled process (cronjob) - Required
    start_command: npm run worker # Executed command when the pod is started - Required
```

### Scales
When you deploy an application in a Kubernetes environment, you define how many replicas you would like to run. 
Each replica represents a Kubernetes POD that encapsulates your application container. 
And also you can increase, or reduce the number of replicas in the given limit.

```yaml
scales:
  my-process:         # Process to scale
    min-replicas: 1   # Minimal number of pods, INTEGER - Required
    max-replicas: 10  # Minimal number of pos, INTEGER - Required
    targetCPUUtilizationPercentage: # Percentage of CPU which will trigger a horizontal scaling when it is exceeded, INTEGER, 0 <= x <= 100 - Required
  another-process: ...
```

### Crons
Crons are tasks that run at a specific time or interval. You can use this type of features to automate tasks, commonly as: reporting, backups, maintenance, emails and so on.

You can define the crons information with the following structure.

```yaml
crons:
  my-cronjob: # Cronjob to define, it must be the same name as the cronjob defined in processes
    concurrency_policy: 'Forbid' # Allow, Forbid or Replace concurrency of cronjobs, STRING - Required. [Kubernetes documentation](https://kubernetes.io/docs/tasks/job/automated-tasks-with-cron-jobs/#concurrency-policy)
    schedule: '* * * * *' # STRING - Required
    suspend:              # BOOLEAN
  another-resource: ...
```

### Resources
This structure defines the resources to be allocated for your application.

```yaml
resources:
  my-resource:  # Name of the resource to define
    limit:
      cpu:      # STRING / NUMBER
      memory:   # STRING
    limits:
      cpu:      # STRING / NUMBER
      memory:   # STRING
    request:
      cpu:      # STRING / NUMBER
      memory:   # STRING
    requests:
      cpu:      # STRING / NUMBER
      memory:   # STRING
  another-resource: ...
```


### TemplateVars
Define variables used in configuration templates when building the kubernetes configuration before deployment. Here are the available variables:

_Note_: All the variables should be prefixed by `tpl`.

```yaml
templateVars:         # Variables used in conf templates
  tplCriticity:       # Define if the app is on the critical path, STRING - high, low, none
  tplPublicServices:  # Define if the application web is public accessible or not, BOOLEAN
  tplExpandedTimeout: # Define the timeout on the ingress controller, STRING
  tplSessionAffinity: # Activate or deactivate session affinity on ingress controller, BOOLEAN
  tplTerminationGracePeriod: # Define POD termination grace period, INTEGER
  tplCanary: # Define name for canary, STRING
```

### Dependencies
The list of dependencies used by your project.

```yaml
dependencies:
  - first-dependency
  - second-dependency
  ...
```

### Public
Determines if the project is publicly available or not 

```yaml
public: true 
```

### Public Aliases
Define aliases for public access.

```yaml
public_aliases:
  - www # STRING
  - api # STRING
  ...
...
```

### Probes

If you need more documentation on what probes are, visit the [official documentation](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-probes).

In this section, you can define some probes Kubernetes for specific containers. Here is the only available probe for the moment:

```yaml
probes:
  web:
    liveness:
      delay: 5  # NUMBER
      path: /   # STRING
```

### Variables

Environment variables used in the application.

```yaml
variables:
  app: # Required
    APP_VAR1: application_variable_1
  ope: # Required
    OPE_VAR1: ope_variable_1
  integration: # The unique env vars (which won't be replaced be staging env vars) belonging to the integration, Optional
    INTEGRATION_VAR1: integration_variable_1
  secret: # Used for secret variables like credentials, Optional
    SECRET_VAR1: secret_variable_1 # WARNING: be careful of using plain-text passwords here.
```


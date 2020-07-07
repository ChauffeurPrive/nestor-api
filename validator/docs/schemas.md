# Configuration Validator

This module contains the logic needed to validate deployment files with a defined schema by Nestor.

The deployment files define applications or projects.

## Table of Contents
1. [Application Configuration](#applicationConfiguration)
2. [Kubernetes Configuration](#kubernetesConfiguration)

<a name="applicationConfiguration"></a>
## Application Configuration

In each file you will define the application that you want to deploy, few fields are required to setup a new application. There are many supported values which are optional that could be useful for your deployment. You can read more about them in the following sections and the schemas definition.

<a name="applicationConfiguration"></a>
#### Application Example 
This is how a basic configuration for an application looks like, this example contains the minimum required fields.

```yaml
app: my-application         # Application's name
is_enabled: false           # Is the application deployment enabled
git: git@microservice_repo  # Git repository URL
variables:                  # Environment variables
  app:                      
    APP_VAR1: application_variable_1
  ope:
    OPE_VAR1: ope_variable_1
```

To further customize the deployment of your application, you can add the following sections to the configuration files.

### Processes

A project can contain multiple processes such as workers, web processes and more.
The structure to define a process is the following one:

```yaml
# Defining a simple process
processes:
  - name: process-name        # Process name - required - maxLength: 58
    is_cronjob: false         # Defining a simple process
    start_command: npm start  # Command executed when the pod is started
# Defining a scheduled process
  - name: cronjob-name
  is_cronjob: true
  start_command: npm run worker
```

### Crons
Crons are tasks that run at a specific time or interval.
You can use them to automate tasks, commonly as: reporting, backups, maintenance, emails and more.

You can define the crons configuration with the following structure.

```yaml
crons:
  my-cronjob: # Cronjob to define, it must be the same name as the cronjob defined in processes
    concurrency_policy: 'Forbid' # Allow, Forbid or Replace concurrency of cronjobs, STRING - Required. [Kubernetes documentation](https://kubernetes.io/docs/tasks/job/automated-tasks-with-cron-jobs/#concurrency-policy)
    schedule: '* * * * *' # STRING - Required
    suspend:              # BOOLEAN
  another-resource:
    schedule: '* * * * *'
    # etc
```

<a name="kubernetesConfiguration"></a>
## Kubernetes Configuration 

### Scales
When you deploy an application in a Kubernetes environment, you define how many replicas you would like to run. 
Each replica represents a Kubernetes Pod that encapsulates your application container. 
And also you can increase, or reduce the number of replicas in the given limit.

```yaml
scales:
  my-process:         # Process to scale
    min-replicas: 1   # Minimal number of pods, INTEGER - Required
    max-replicas: 10  # Minimal number of pods, INTEGER - Required
    targetCPUUtilizationPercentage: 80 # Percentage of CPU which will trigger a horizontal scaling when it is exceeded, INTEGER, 0 <= x <= 100 - Required
  another-process: 
    min-replicas: 1
    max-replicas: 5
    targetCPUUtilizationPercentage: 95
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

Kubernetes has service settings to allow to expose an application running on a set of Pods as a network service. The idea is that Kubernetes handles the network layer to provide IP addresses to your Pods and a single DNS name for a set of Pods and can load-balance across them. You can read more in [the official Kubernetes documentation](https://kubernetes.io/docs/concepts/services-networking/).

In this section you can define variables used in configuration templates when building the kubernetes configuration before deployment. Here are the available variables:

**_Note_**: All the variables should be prefixed by `tpl`. To avoid colliding with the 

```yaml
templateVars:         # Variables used in conf templates
  tplCriticity:       # Define if the app is on the critical path, STRING - high, low, none
  tplPublicServices:  # Define if the application web is public accessible or not, BOOLEAN
  tplExpandedTimeout: # Define the timeout on the ingress controller, STRING
  tplSessionAffinity: # Activate or deactivate session affinity on ingress controller, BOOLEAN
  tplTerminationGracePeriod: # Define POD termination grace period, INTEGER
  tplCanary:          # Define name for canary, STRING
```

### Dependencies

This section can be used when your application depends or makes use of another applications. In this section you can specify the list dependencies used by your project. 

```yaml
dependencies:
  - api-v1
  - voice-service
  - payment-service
  # .. and more
  # if your application does not have dependencies, you can omit this section
```

### Public
Determines if the project is publicly available for other services in your kubernetes namespace, this will allow internal interaction between applications.

```yaml
public: true 
```

### Public Aliases
In this section allows at pod-level to override the hostname resolution when DNS and other options are not applicable. This is a feature of Kubernetes, that allows to reach your application with a more friendly name.

You can define an alias for your application to facilitate public access.

If you need further documentation of how DNS and the network layer works in Kubernets. We recommend you to read [the official Kubernetes documentation](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)

```yaml
public_aliases:
  - www # STRING
  - api # STRING
```

### Probes

In this section, you can define some Kubernetes' probes for the web process. It is currently not possible to define probes for other processes.

```yaml
probes:
  web:
    liveness:
      delay: 20         # NUMBER
      path: /heartbeat  # STRING
```

**_Note_**: If you need more documentation on what probes are and their usage, visit the [official Kubernetes documentation](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-probes).

### Variables
There are two categories of environment variables that you can add to your application: `ope` and `app`. 

The idea is to separate concerns between the variables that your application needs.

- `ope`: These are used to specify operational values such as URLs, certificates, auth public keys, connection strings, integration with third party services and other services information used by your app.
- `app`: These are the variables used internally for adding logic to the application, such as: fixed values, timeouts, default values, feature flags, ids, and more.


Environment variables used in the application.

```yaml
variables:
  app: # Required
    LOG_LEVEL: info
    API_TIMEOUT: 10000 
  ope: # Required
    DB_CONNECTION_STRING: mongodb://user:password@server:27017
  secret: # Used for secret variables like credentials (optional)
    SECRET_VAR1: secret_variable_1 # WARNING: be careful of using plain-text passwords here.
```


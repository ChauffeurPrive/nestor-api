# Nestor workflow

## Context

Nestor workflow is used to manage the progression of a commit through your release process, from the development environment to the production release of an application.  
It is composed of multiple steps, each step following the previous one.

## Setup

Nestor workflow is defined in [nestor configuration](TODO Link to doc), using a list, for example:

```yaml
workflow:
  - master
  - staging
  - production
```

Each step is linked to a dedicated branch on your application repository.

The steps' **order matters**.  
The first one matches the branch on which the commits you want to release will be merged (it can be your `master` branch for instance).
Each step defined after that corresponds to an environment on which the commit will be deployed via the workflow.
From this point, it is up to you to, either configure your CI, or schedule a job in order to make the workflow go from one step to another at the desired frequency.

## Usage

TODO: Detail routes used to make the workflow advance

## Details

Nestor workflow relies on commit hashes. When trying to make the workflow go forward, it compares the previous step's most recent commit hash with the one from the step we want to move forward to:

- if they differs, this means that the previous step has new commits that need to be applied on the next step
- if commit hashes are the same, the two steps (branches) are in sync, there is nothing to do

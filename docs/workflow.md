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

Each step is linked to a dedicated branch on your application repo.  
The steps **order matters**. The first one matches the branch on which your commits are merged and will trigger the rest of the workflow, through CI hooks. Then, each step represent an environment on which the commit will be deployed.

## Usage

TODO: Detail routes used to make the workflow advance

## Details

Nestor workflow relies on commit hashes. When trying to make the workflow go forward, we compare the previous step most recent commit hash with the one from the step we want to move forward:

- if they differs, this means that the previous step has new commits that need to be applied on the next step
- if commit hashes are the same, the two steps (branches) are in sync, there is nothing to do

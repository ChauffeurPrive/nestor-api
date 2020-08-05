# Getting started

## Prerequisites

### Git repositories

<a name="github-account-prerequisite"></a>
Create an account with sufficient permissions to be able to merge on protected branches using the workflow features.

**Supported host:** GitHub

## Configuration

### Build

You should create a hook triggered every time new commits are merged on the first step of your workflow (e.g. master) calling [Nestor's build API](./api.md#api-build-api).

This will create a new docker image corresponding to this new version.

Nestor will tag this image with a reference to the version of your application and the commit hash before pushing it to your Docker registry.

**This will guarantee that you are using the same version for all environment.**

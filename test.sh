#!/bin/bash

set -x

PAT=$1

echo build unit under test
podman build -t glvd-triage-cli-integration-test .

echo bring up database instance
podman compose up -d

# fixme(fwilhe): properly await that the db is up
sleep 15

echo fill db instance with schema
podman run -it --rm --network=glvd-triage-cli_glvd-triage-IT --env PGHOST=glvd-postgres ghcr.io/gardenlinux/glvd-init:latest

echo run test
podman run -it --rm --network=glvd-triage-cli_glvd-triage-IT --env PGHOST=glvd-postgres --env PAT=$PAT localhost/glvd-triage-cli-integration-test:latest

# fixme(fwilhe): some sort of asserts

#!/bin/bash

podman compose --file integration-test-compose.yaml up --build --force-recreate

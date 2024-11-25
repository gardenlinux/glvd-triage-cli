#!/bin/bash

echo "$PGHOST:$PGPORT:$PGDATABASE:$PGUSER:$PGPASSWORD" > ~/.pgpass
chmod 0600 ~/.pgpass

wcurl https://raw.githubusercontent.com/gardenlinux/glvd-triage-data/refs/heads/main/sample.yaml

python3 /cli.py > /triage.sql

ls -l /triage.sql
cat /triage.sql

psql glvd -f /triage.sql

#!/bin/bash

echo "$PGHOST:$PGPORT:$PGDATABASE:$PGUSER:$PGPASSWORD" > ~/.pgpass
chmod 0600 ~/.pgpass

git clone --depth=1 https://github.com/gardenlinux/glvd-triage-data /data/

python3 /cli.py > /triage.sql

ls -l /triage.sql
cat /triage.sql

psql glvd -f /triage.sql

#!/bin/bash

echo "$PGHOST:$PGPORT:$PGDATABASE:$PGUSER:$PGPASSWORD" > ~/.pgpass
chmod 0600 ~/.pgpass

if [[ $PAT == "NOT_SET" ]]; then
    if [[ -f /run/secrets/github_pat ]]; then
        PAT=$(cat /run/secrets/github_pat)
    else
        echo GitHub PAT not set.
        exit 1
    fi
fi

git clone --depth=1 https://"$PAT"@github.com/gardenlinux/glvd-triage-data /data/

python3 /cli.py > /triage.sql

ls -l /triage.sql
cat /triage.sql

psql glvd -f /triage.sql

psql -c "select * from public.cve_context where create_date > now() - interval '1 day';" glvd

#!/bin/bash

echo "$PGHOST:$PGPORT:$PGDATABASE:$PGUSER:$PGPASSWORD" > ~/.pgpass
chmod 0600 ~/.pgpass

# todo(fwilhe): better assertions, more stable and useful test data

psql -c "select * from public.cve_context where create_date > now() - interval '1 day';" glvd > /tmp/results.txt

if grep -q -E 'CVE-2024-10979|CVE-2024-10977|CVE-2024-10978|CVE-2024-53051' /tmp/results.txt; then
    echo "ok"
else
    echo fail
    exit 1
fi

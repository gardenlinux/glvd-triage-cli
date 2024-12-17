#!/bin/bash

echo "$PGHOST:$PGPORT:$PGDATABASE:$PGUSER:$PGPASSWORD" > ~/.pgpass
chmod 0600 ~/.pgpass

psql -c "select * from public.cve_context where create_date > now() - interval '1 day';" glvd > /tmp/results.txt

if grep -q 'CVE-' /tmp/results.txt; then
  echo "ok"
fi

#!/bin/bash

echo "$PGHOST:$PGPORT:$PGDATABASE:$PGUSER:$PGPASSWORD" > ~/.pgpass
chmod 0600 ~/.pgpass

# todo(fwilhe): better assertions, more stable and useful test data

if [ "pre" == "$1" ]; then
    psql -c "select * from public.cve_context where create_date > now() - interval '1 day';" glvd > /tmp/results.txt
    cat /tmp/results.txt
    wc -l /tmp/results.txt
    # Assert CVEs are not triaged
    if grep -q -E 'CVE-2024-53142|CVE-2024-53141|CVE-2024-50106|CVE-2024-56201' /tmp/results.txt; then
        echo fail
        exit 1
    else
        echo "ok"
    fi
fi

if [ "post" == "$1" ]; then
    psql -c "select * from public.cve_context where create_date > now() - interval '1 day';" glvd > /tmp/results.txt
    cat /tmp/results.txt
    wc -l /tmp/results.txt
    # Assert CVEs are triaged
    if grep -q -E 'CVE-2024-53142|CVE-2024-53141|CVE-2024-50106|CVE-2024-56201' /tmp/results.txt; then
        echo "ok"
    else
        echo fail
        exit 1
    fi
fi

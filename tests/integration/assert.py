import os
import psycopg2
import pytest

# Define the expected rows as tuples (order and types must match the DB schema)
EXPECTED_ROWS = [
    (
        15, "today", "CVE-2023-50387",
        "gardener", None, "automated dummy data\n", True, 1, False
    ),
    (
        17, "1592.5", "CVE-2025-0938",
        "all", None, "Unit test for https://github.com/gardenlinux/glvd/issues/141\n", True, 2, False
    ),
    (
        17, "1592.5", "CVE-2024-11053",
        "gardener", None, 
        "#### Vulnerability Description:\nA potential buffer overflow was identified in the `curl` library that could allow a malicious server to craft a response causing arbitrary code execution. This vulnerability occurs when certain functions do not adequately check the length of data being processed during an HTTP response header parsing operation. If exploited, this could lead to severe system compromise.\n\n#### False Positive Reasoning:\nThis issue might be flagged as a vulnerability even when using a patched version of `curl`, as some vulnerability scanners rely on version strings rather than actual behavior. For example, a patched `curl` version running on a backported Linux distribution might still report the version as vulnerable. Moreover, if features that rely on the affected codepath (e.g., HTTP) are disabled at compile-time, the vulnerability is not exploitable.\n\n#### Additional Comments:\nAnother potential false positive arises when software dynamically links against `libcurl`, and only specific binaries trigger the vulnerable behavior. If the primary application does not invoke the affected API calls, the flagged vulnerability is functionally irrelevant. Verifying usage paths and runtime configuration can often clear up the status.\n",
        False, 3, False
    ),
    (
        17, "1592.5", "CVE-2024-12085",
        "gardener", None, 
        "#### Vulnerability Description:\nA critical flaw was discovered in `rsync` that relates to improper validation of symbolic links when handling file synchronization from remote sources. This vulnerability could allow a malicious actor to exploit directory traversal and overwrite critical system files. The attack is particularly concerning when rsync is used in daemon mode with insufficient sanitization.\n\n#### False Positive Reasoning:\nThis vulnerability may appear as a false positive in configurations where strict chroot and privilege separation are enforced. For example, environments where access controls are properly implemented in the `rsyncd.conf` file might mitigate the risk entirely. Additionally, users often operate `rsync` with `--safe-links`, which disallows following unsafe symbolic links, negating the potential exploitation.\n\n#### Additional Comments:\nAnother contributing factor to false positives is the presence of mitigations at the kernel or file system level. Systems that enforce AppArmor or SELinux policies restricting file write permissions from external processes might render the reported issue non-exploitable. Testing the setup under actual conditions can often help determine its true relevance.\n",
        False, 4, False
    ),
]

def get_connection():
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "glvd"),
        user=os.environ.get("PGUSER", "glvd"),
        password=os.environ.get("PGPASSWORD", "glvd"),
    )

@pytest.mark.parametrize("expected_row", EXPECTED_ROWS)
def test_cve_context_row_exists(expected_row):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Build a query that matches all fields
            cur.execute("""
                SELECT COUNT(*) FROM cve_context
                WHERE dist_id = %s
                  AND gardenlinux_version = %s
                  AND cve_id = %s
                  AND use_case = %s
                  AND score_override IS NOT DISTINCT FROM %s
                  AND description = %s
                  AND is_resolved = %s
                  AND id = %s
                  AND triaged = %s
            """, expected_row)
            count = cur.fetchone()[0]
            assert count == 1, f"Row not found or not unique: {expected_row}"
    finally:
        conn.close()

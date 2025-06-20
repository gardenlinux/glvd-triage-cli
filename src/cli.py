import yaml
import psycopg2
from psycopg2.extras import execute_values

import argparse

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "glvd",
    "user": "glvd",
    "password": "glvd"
}

TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS cve_context2 (
    id SERIAL PRIMARY KEY,
    revision TEXT NOT NULL,
    cve TEXT NOT NULL,
    dist TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL,
    triaged BOOLEAN NOT NULL,
    description TEXT,
    use_case TEXT,
    score_override FLOAT,
    ignored BOOLEAN,
    patch TEXT,
    patched_version TEXT,
    name TEXT,
    reason TEXT,
    scope TEXT,
    version TEXT,
    gl_version TEXT
);
"""

def parse_yaml_file(filepath):
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise ValueError("YAML root must be a list")
    return data

def to_db_rows(entry):
    cves = entry.get("cves", [])
    dists = entry.get("dists", [])
    if not cves or not dists:
        cves = cves or [None]
        dists = dists or [None]
    rows = []
    for cve in cves:
        for dist in dists:
            rows.append((
                entry.get("revision"),
                cve,
                dist,
                entry.get("is_resolved", False),
                entry.get("triaged", False),
                entry.get("description"),
                entry.get("use-case"),
                entry.get("score_override"),
                entry.get("ignored", False),
                entry.get("patch"),
                entry.get("patched_version"),
                entry.get("name"),
                entry.get("reason"),
                entry.get("scope"),
                entry.get("version"),
                entry.get("gl_version"),
            ))
    return rows

def main(yaml_path, dry_run=False):
    entries = parse_yaml_file(yaml_path)
    all_rows = []
    for entry in entries:
        all_rows.extend(to_db_rows(entry))

    if dry_run:
        print(f"DRY RUN: Would insert {len(all_rows)} rows into cve_context2 table.")
        for row in all_rows:
            print(row)
        return

    conn = psycopg2.connect(**DB_CONFIG)
    with conn:
        with conn.cursor() as cur:
            cur.execute(TABLE_SCHEMA)
            insert_sql = """
                INSERT INTO cve_context2 (
                    revision, cve, dist, is_resolved, triaged, description,
                    use_case, score_override, ignored, patch, patched_version,
                    name, reason, scope, version, gl_version
                ) VALUES %s
                ON CONFLICT DO NOTHING
            """
            execute_values(cur, insert_sql, all_rows)
    print(f"Inserted {len(all_rows)} rows into cve_context2 table.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse triage YAML and store in Postgres.")
    parser.add_argument("yaml_file", help="Path to triage YAML file")
    parser.add_argument("--dry-run", action="store_true", help="Print rows instead of writing to DB")
    args = parser.parse_args()
    main(args.yaml_file, dry_run=args.dry_run)

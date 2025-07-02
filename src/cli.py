import yaml
import psycopg2
from psycopg2.extras import execute_values
import urllib.request

import argparse
import os

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": int(os.environ.get("PGPORT", 5432)),
    "dbname": os.environ.get("PGDATABASE", "glvd"),
    "user": os.environ.get("PGUSER", "glvd"),
    "password": os.environ.get("PGPASSWORD", "glvd")
}

gl_version_to_dist_id_mapping = {}

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
            dist_id = gl_version_to_dist_id_mapping.get(dist, -1)
            if dist_id == -1:
                dist_id = int(urllib.request.urlopen(f"https://glvd.ingress.glvd.gardnlinux.shoot.canary.k8s-hana.ondemand.com/v1/distro/{dist}/distId").read().decode("utf-8"))
                gl_version_to_dist_id_mapping[dist] = dist_id

            rows.append((
                dist_id,
                dist,
                cve,
                entry.get("use_case"),
                entry.get("score_override"),
                entry.get("description"),
                entry.get("is_resolved", False),
                entry.get("triaged", False)
            ))
    return rows

def main(yaml_path, dry_run=False):
    entries = parse_yaml_file(yaml_path)
    all_rows = []
    for entry in entries:
        all_rows.extend(to_db_rows(entry))

    if dry_run:
        print(f"DRY RUN: Would insert {len(all_rows)} rows into public.cve_context table.")
        for row in all_rows:
            print(row)
        return

    conn = psycopg2.connect(**DB_CONFIG)
    with conn:
        with conn.cursor() as cur:
            insert_sql = """
                INSERT INTO public.cve_context (
                    dist_id, gardenlinux_version, cve_id, use_case, score_override, description, is_resolved, triaged
                ) VALUES %s
                ON CONFLICT DO NOTHING
            """
            execute_values(cur, insert_sql, all_rows)
    print(f"Inserted {len(all_rows)} rows into public.cve_context table.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse triage YAML and store in Postgres.")
    parser.add_argument("yaml_file", help="Path to triage YAML file")
    parser.add_argument("--dry-run", action="store_true", help="Print rows instead of writing to DB")
    args = parser.parse_args()
    main(args.yaml_file, dry_run=args.dry_run)

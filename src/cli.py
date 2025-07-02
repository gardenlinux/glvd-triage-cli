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
        print(f"Error in {filepath}: YAML root must be a list")
        return {}
    return data

def to_db_rows_v1(entry):
    cves = entry.get("cves", [])
    dists = entry.get("dists", [])
    if not cves or not dists:
        cves = cves or [None]
        dists = dists or [None]
    rows = []
    for cve in cves:
        # Ignore non-CVE entries for now as GLVD does not support anything else
        if not str.startswith(cve, 'CVE-'):
            continue
        for dist in dists:
            print(dist)
            print(gl_version_to_dist_id_mapping)
            dist_id = gl_version_to_dist_id_mapping.get(dist, -1)
            
            try:
                if dist_id == -1:
                    dist_id = int(urllib.request.urlopen(f"https://glvd.ingress.glvd.gardnlinux.shoot.canary.k8s-hana.ondemand.com/v1/distro/{dist}/distId").read().decode("utf-8"))
                    gl_version_to_dist_id_mapping[dist] = dist_id

                rows.append((
                    dist_id,
                    dist,
                    cve,
                    entry.get("use_case", "all"),
                    entry.get("score_override"),
                    entry.get("description"),
                    entry.get("is_resolved", False),
                    entry.get("triaged", False)
                ))
            except:
                print(f"Can't resolve dist {dist}, skipping entry")
    return rows

def main(yaml_dir, dry_run=False):
    yaml_files = []
    for root, dirs, files in os.walk(yaml_dir):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                yaml_files.append(os.path.join(root, file))
    all_rows = []
    for yaml_path in yaml_files:
        entries = parse_yaml_file(yaml_path)
        for entry in entries:
            if entry.get('revision', 'v0') == 'v1':
                print(entry)
                all_rows.extend(to_db_rows_v1(entry))
            else:
                print(f'revision {entry.get('revision', 'v0')} is not implemented')

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
    parser = argparse.ArgumentParser(description="Parse triage YAML files in a directory and store in Postgres.")
    parser.add_argument("yaml_dir", help="Path to directory containing triage YAML files")
    parser.add_argument("--dry-run", action="store_true", help="Print rows instead of writing to DB")
    args = parser.parse_args()
    main(args.yaml_dir, dry_run=args.dry_run)

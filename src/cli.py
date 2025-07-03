import yaml
import psycopg2
from psycopg2.extras import execute_values
import urllib.request

import argparse
import os

import logging
logger = logging.getLogger("glvd-triage-cli")
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

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
        logger.warning(f"Error in {filepath}: YAML root must be a list")
        return {}
    return data


def gardenlinux_version_to_distId_resolver(gardenlinux_version):
    url = f"https://glvd.ingress.glvd.gardnlinux.shoot.canary.k8s-hana.ondemand.com/v1/distro/{gardenlinux_version}/distId"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status != 200:
                logger.error(f"Failed to fetch distId for {gardenlinux_version}: HTTP {response.status}")
                return -1
            data = response.read().decode("utf-8")
            return int(data)
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP error while fetching distId for {gardenlinux_version}: {e}")
    except urllib.error.URLError as e:
        logger.error(f"URL error while fetching distId for {gardenlinux_version}: {e}")
    except ValueError as e:
        logger.error(f"Invalid distId received for {gardenlinux_version}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching distId for {gardenlinux_version}: {e}")
    return -1


def to_db_rows_v1(entry, distId_resolver):
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
            logger.debug(f"Processing dist {dist}")
            logger.debug(f"Current dist to distId mapping {gl_version_to_dist_id_mapping}")
            dist_id = gl_version_to_dist_id_mapping.get(dist, -1)
            
            try:
                if dist_id == -1:
                    dist_id = distId_resolver(dist)
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
                logger.warning(f"Can't resolve dist {dist}, skipping entry")
    return rows

def main(yaml_dir, dry_run=False):
    yaml_files = []
    for root, dirs, files in os.walk(yaml_dir):
        for file in files:
            logger.debug(f'file: {file}')
            if file.endswith(".yaml") or file.endswith(".yml"):
                logger.debug(f'file: {os.path.join(root, file)}')
                yaml_files.append(os.path.join(root, file))
    all_rows = []
    for yaml_path in yaml_files:
        entries = parse_yaml_file(yaml_path)
        for entry in entries:
            if entry.get('revision', 'v0') == 'v1':
                logger.debug(entry)
                all_rows.extend(to_db_rows_v1(entry, gardenlinux_version_to_distId_resolver))
            else:
                logger.warning(f'revision {entry.get('revision', 'v0')} is not implemented')

    if dry_run:
        logger.info(f"DRY RUN: Would insert {len(all_rows)} rows into public.cve_context table.")
        for row in all_rows:
            logger.info(row)
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
    logger.info(f"Inserted {len(all_rows)} rows into public.cve_context table.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse triage YAML files in a directory and store in Postgres.")
    parser.add_argument("yaml_dir", help="Path to directory containing triage YAML files")
    parser.add_argument("--dry-run", action="store_true", help="Print rows instead of writing to DB")
    args = parser.parse_args()
    logger.debug(f'yaml_dir: {args.yaml_dir}')
    logger.debug(f'dry_run: {args.dry_run}')
    main(args.yaml_dir, dry_run=args.dry_run)

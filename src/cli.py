import yaml
import json
import os
import os.path

dist_id_mapping = {}



# Default values for optional fields
DEFAULTS = {
    "is_resolved": False,
    "triaged": False,
    "ignored": False,
    "scope": None,
    "descriptor": None,
    "score_override": None,
    "name": None,
    "reason": None,
    "version": None,
    "gl_version": None,
    "description": None,
}

def parse_yaml(file_path):
    """
    Parses a YAML file and applies default values for optional fields.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        list: A list of parsed and validated entries.
    """
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, list):
        raise ValueError("The YAML file must contain a list of entries.")

    parsed_entries = []
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError("Each entry in the YAML file must be a dictionary.")

        # Validate required fields
        for required_field in ["format", "cves", "dists"]:
            if required_field not in entry:
                raise ValueError(f"Missing required field: {required_field}")

        # Apply default values for optional fields
        parsed_entry = {key: entry.get(key, DEFAULTS.get(key)) for key in DEFAULTS}
        parsed_entry.update({key: entry[key] for key in entry if key not in DEFAULTS})

        # Validate specific fields
        if parsed_entry["format"] != "v1alpha1":
            raise ValueError(f"Unsupported format: {parsed_entry['format']}")
        if not isinstance(parsed_entry["cves"], list) or not all(isinstance(cve, str) for cve in parsed_entry["cves"]):
            raise ValueError("The 'cves' field must be a list of strings.")
        if not isinstance(parsed_entry["dists"], list) or not all(isinstance(dist, str) for dist in parsed_entry["dists"]):
            raise ValueError("The 'dists' field must be a list of strings.")

        parsed_entries.append(parsed_entry)

    return parsed_entries


def main():
    with open('dist_cpe.json') as dist:
        dist_id_mapping = json.loads(dist.read())

    file = f"/data/{os.environ['GLVD_TRIAGE_FILE']}"
    if not os.path.isfile(file):
        raise Exception(f"{file} is not a file")
    items = yaml.load(open(file), Loader=yaml.FullLoader)

    for item in items:
        dists = item['dists']
        for dist in dists:
            dist_id = dist_id_mapping[dist]

            cves = item['cves']
            for cve in cves:
                descriptor = item.get('descriptor', 'GARDENER')
                description = item.get('description', 'not provided')
                is_resolved = str(item.get('is_resolved', 'false')).lower()
                score_override = item.get('score_override', 'NULL')
                stmt = f"INSERT INTO public.cve_context (dist_id, cve_id, context_descriptor, score_override, description, is_resolved) VALUES('{dist_id}', '{cve}', '{descriptor}', {score_override}, '{description}', {is_resolved});"

                print(stmt)

if __name__ == "__main__":
    main()

import yaml
import json
import os
import os.path

dist_id_mapping = {}


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

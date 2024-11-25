import yaml

# very rough prototype
# purpose:
# take triage/cve context data from a yaml file and insert it into the glvd db

def main():
    items = yaml.load(open('sample.yaml'), Loader=yaml.FullLoader)

    dist_id_mapping = {
        'today': 14
    }

    for item in items:
        dists = item['dists']
        for dist in dists:
            dist_id = dist_id_mapping[dist]

            cves = item['cves']
            for cve in cves:
                descriptor = item.get('descriptor', 'GARDENER')
                description = item.get('description', 'not provided')
                is_resolved = str(item.get('is_resolved', 'false')).lower()
                stmt = f"INSERT INTO public.cve_context (dist_id, cve_id, context_descriptor, description, is_resolved) VALUES('{dist_id}', '{cve}', '{descriptor}', '{description}', {is_resolved});"

                print(stmt)

if __name__ == "__main__":
    main()

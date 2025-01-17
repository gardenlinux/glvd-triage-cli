import csv
import json

mapping = {}

with open('dist_cpe.csv', newline='') as dist_mapping:
    foo = csv.reader(dist_mapping, delimiter=',')
    for row in foo:
        dist_id = row[0]
        dist_name = row[2]
        dist_version = row[3]
        if dist_name == 'gardenlinux':
            mapping[dist_version] = dist_id

with open('dist_cpe.json', 'w+') as dist_mapping_json:
    dist_mapping_json.write(json.dumps(mapping))

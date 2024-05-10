import json
import os

coverage = dict()

dir_path = './coverages'
output_path = './coverage.json'
for file_name in os.listdir(dir_path):
    if file_name.endswith('.json'):
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'r') as f:
            data = json.load(f)
            coverage.update(data)

with open(output_path, 'w') as wf:
    json.dump(coverage, wf, indent = 4)

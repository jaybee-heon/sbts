import json

real_file_path = './data/killmap/Time-1_fdr.json'
extra_file_path = './data/killmap/Time-1_fdr_4.json'
output_file_path = './data/killmap/Time-1_fdr.json'

with open(real_file_path, 'r') as f:
    original_data = json.load(f)

with open(extra_file_path, 'r') as f:
    extra_data = json.load(f)

extra_keys = extra_data['Time_1'].keys()
original_keys = original_data['Time_1'].keys()

for key in extra_keys:
    if key not in original_keys:
        original_data['Time_1'][key] =  extra_data['Time_1'][key]

with open(output_file_path, 'w') as f:
    json.dump(original_data, f, indent = 4)

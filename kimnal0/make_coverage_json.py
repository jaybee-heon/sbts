import json
import os

merged_data = {"JxPath_22": {}}

dir_path = './mutation/JxPath-22'
output_path = '../data/all_class_mutation/JxPath-22_fdr.json'

for file_name in os.listdir(dir_path):
    if file_name.endswith('.json'):
        file_path = os.path.join(dir_path, file_name)

        ## For coverge
        # with open(file_path, 'r') as f:
        #     data = json.load(f)
        #     mutation.update(data)
        #     for key in mutation.keys():
        #         print(len(mutation[key]))
        #     print()

        ## for mutation
        print(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            
            data = json.load(file)
            if "JxPath_22" in data:
                for key, value in data["JxPath_22"].items():
                    merged_data["JxPath_22"][key] = value

with open(output_path, 'w') as wf:
    json.dump(merged_data, wf, indent = 4)

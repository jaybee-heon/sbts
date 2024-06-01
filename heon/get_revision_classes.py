from datetime import datetime
import json
from pathlib import Path

dir_path = Path("../data/revision_info")
file_list = list(dir_path.iterdir())
for file in file_list:
    project_id = file.name.split("_revision_info.txt")[0]
    revision_info = []
    with open(file, 'r', encoding='utf-8') as file:
        for line in file:
            if len(line) < 1:
                continue
            items = line.split(",")
            version_id = items[0]
            revision_date = items[1].strip()
            classes = items[2].strip().replace("\"", '').split(";")
            revision_info.append([revision_date, classes])

    class_to_revisions = dict()
    revision_info = sorted(revision_info, key=lambda x: x[0])
    for idx, revision in enumerate(revision_info):
        revision_date = revision[0]
        revision_classes = revision[1]
        for klass in revision_classes:
            if klass not in class_to_revisions:
                class_to_revisions[klass] = []
            class_to_revisions[klass].append({"latest_idx": idx, "revision_date": revision_date})

    json_file_path = f"../data/revision_history_by_class/{project_id}.json"
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(class_to_revisions, json_file, indent=4)

    print(f"Data has been successfully saved to {json_file_path}")
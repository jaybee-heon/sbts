import json

# 읽을 JSON 파일들의 경로
file_paths = [
    './all_class_mutation/Chart-1_fdr_0.json',
    './all_class_mutation/Chart-1_fdr_1.json',
    './all_class_mutation/Chart-1_fdr_2.json',
    './all_class_mutation/Chart-1_fdr_3.json'
]
merged_data = []

# 각 JSON 파일을 읽어서 병합
merged_data = {"Chart_1": {}}

# 각 JSON 파일을 읽어서 병합
for file_path in file_paths:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        if "Chart_1" in data:
            for key, value in data["Chart_1"].items():
                merged_data["Chart_1"][key] = value

# 병합된 데이터를 새로운 JSON 파일로 저장
with open('./Chart-1_fdr.json', 'w', encoding='utf-8') as merged_file:
    json.dump(merged_data, merged_file, ensure_ascii=False, indent=4)

print("JSON 파일이 성공적으로 병합되었습니다.")

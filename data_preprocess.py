import numpy as np
import pandas as pd
import json

# # Load JSON data
file_path = "data/tet.json"
''' 
    json file 을 Pandas DataFrame 으로 변환하는 함수입니다. 
    data = {
        "project1": {"bug1": 1, "bug2": 2},
        "project2": {"bug1": 5, "bug2": 6},
    }
'''
# def json2PandasDf(file_path):
    
#     with open(file_path, 'r') as file:
#         data = json.load(file)

#     dataset = {}
#     # Print out the arrays
#     for key, value in data.items():
#         df = pd.DataFrame.from_dict(value, orient='index')
#         dataset[key] = df
#         print(f"Table: {key}"
#             f"\n{df}")
#     return dataset

import json
import os
import glob
import pandas as pd 

### data 폴더에 있는 각 project 들에 대한 fault detection 파일을 읽어 하나의 파일로 만듦.
def make_all_fdr():
    # Directory containing JSON files
    directory = 'data/all_class_mutation'

    # Initialize an empty dictionary to store the concatenated results
    concatenated_results = {}
    skipped_files = ['JacksonDatabind-112_fdr.json']

    # Iterate over each JSON file in the directory
    for filepath in glob.glob(os.path.join(directory, '*.json')):
        
        if os.path.basename(filepath) in skipped_files:
            print(f"Skipping {filepath}")               ## mutation score 가 없는 테스트들이 있는 파일은 스킵합니다. 
            continue
        
        with open(filepath, 'r') as file:
            data = json.load(file)
            for key, value in data.items():
                if key not in concatenated_results:
                    concatenated_results[key] = {}
                for subkey, subvalue in value.items():
                    if 'mutation-score' not in subvalue:
                        print(f"Warning: mutation-score not found in {filepath} ")
                        continue
                    concatenated_results[key][subkey] = subvalue['mutation-score']

    json.dump(concatenated_results, open('data/all_fdr.json', 'w'), indent=4)
    # Convert the flattened data to a DataFrame
    
def _rename_keys(d):
    if isinstance(d, dict):
        new_dict = {}
        for k, v in d.items():
            new_key = k.replace("-", "_")
            new_dict[new_key] = _rename_keys(v)
        return new_dict
    elif isinstance(d, list):
        return [_rename_keys(i) for i in d]
    else:
        return d
    
''' 
    project 별로 fdr, coverage, tet 파일을 읽어 dataframe 으로 만들고, 
    project 들의 데이터 프레임을 담은 리스트를 반환합니다. 
'''
def merge_fdr_coverage_tet(fdr_path, coverage_path, tet_path, save_excel=True):  
    # Load the JSON 
    with open(fdr_path, 'r') as  file1 , open(coverage_path, 'r') as file2, open(tet_path, 'r') as file3:
        fdr_data = json.load(file1)
        coverage_data = json.load(file2) 
        tet_data = json.load(file3)
    
    merged_data = {}
    projects = {}

    ## project 이름을 통일시켜줍니다. "Time-1" => "Time_1"  
    fdr_data = _rename_keys(fdr_data)
    coverage_data = _rename_keys(coverage_data)
    tet_data = _rename_keys(tet_data)
    
    fdr_keys = set(fdr_data.keys())
    coverage_keys = set(coverage_data.keys())  
    tet_keys = set(tet_data.keys())

    ## fdr, coverage, tet 이 모두 있는 project 만 선택합니다.
    all_keys = fdr_keys.intersection(coverage_keys).intersection(tet_keys)
    for key in all_keys:
        df1 = pd.DataFrame.from_dict(fdr_data.get(key, {}), orient='index').rename(columns={0: 'fdr'})
        df2 = pd.DataFrame.from_dict(coverage_data.get(key, {}), orient='index').rename(columns={0: 'coverage'})
        df3 = pd.DataFrame.from_dict(tet_data.get(key, {}), orient='index').rename(columns={0: 'tet'})
        merged_df = pd.concat([df1, df2, df3], axis=1, join='inner')
        projects[key] = merged_df

        if save_excel:  ## excel 로 저장하고 싶으면 저장
            output_dir = './data/excel'
            merged_df.to_excel(os.path.join(output_dir, f'{key}.xlsx'))
                
    return projects

if __name__ == "__main__":
    make_all_fdr()  ## data/all_fdr.json 파일을 생성합니다.
    
    fdr_path = "./data/all_fdr.json"
    coverage_path = "./data/all_coverage.json"
    tet_path = "./data/tet.json"
    merge_fdr_coverage_tet(fdr_path, coverage_path, tet_path, verbose=False) ## data 폴더에 merged_*.json 파일을 생성합니다.
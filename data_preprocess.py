import numpy as np
import pandas as pd
import json
import pickle
import os
import glob

# # Load JSON data
file_path = "data/tet.json"
''' 
    json file 을 Pandas DataFrame 으로 변환하는 함수입니다. 
    data = {
        "project1": {"bug1": 1, "bug2": 2},
        "project2": {"bug1": 5, "bug2": 6},
    }
'''
def json2PandasDf(file_path):
    
    with open(file_path, 'r') as file:
        data = json.load(file)

    dataset = {}
    # Print out the arrays
    for key, value in data.items():
        df = pd.DataFrame.from_dict(value, orient='index')
        dataset[key] = df
        print(f"Table: {key}"
            f"\n{df}")
    return dataset

def merge_history_and_covered():
    # Load the JSON files
    with open('data/coverage/covered_class_test_pairs.json') as f1:
        data1 = json.load(f1)

    # Initialize an empty DataFrame to store the results
    final_result_df = pd.DataFrame()

    # Process each revision history file
    for file in os.listdir('data/revision_history_by_class'):
        if file.endswith('.json'):
            with open(f'data/revision_history_by_class/{file}') as f2:
                data2 = json.load(f2)

            # Normalize and process data from file1.json
            records = []
            for project, tests in data1.items():
                for test, classes in tests.items():
                    for cls in classes:
                        records.append({'projectName': project, 'testName': test, 'className': cls})

            df1 = pd.DataFrame(records)

            # Normalize and process data from file2.json
            records = []
            for cls, revisions in data2.items():
                for revision in revisions:
                    record = {'className': cls, 'latest_idx': revision['latest_idx']}
                    records.append(record)

            df2 = pd.DataFrame(records)

            # Merge DataFrames on className
            merged_df = pd.merge(df1, df2, on='className')

            # Group by projectName and testName, then calculate the sum of latest_idx
            result_df = merged_df.groupby(['projectName', 'testName'])['latest_idx'].sum().reset_index()

            # Concatenate the result_df to final_result_df
            final_result_df = pd.concat([final_result_df, result_df])

    # Save the final concatenated DataFrame to a JSON file in the required format
    result_dict = {}
    for index, row in final_result_df.iterrows():
        project = row['projectName']
        test = row['testName']
        idx_sum = row['latest_idx']
        
        if project not in result_dict:
            result_dict[project] = {}
        result_dict[project][test] = 1/idx_sum

    # Save the result to a JSON file
    with open('data/final_result.json', 'w') as outfile:
        json.dump(result_dict, outfile, indent=4)

    # Print the result to verify


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
def merge_all_data(fdr_path, coverage_path, tet_path, fixed_line_cov_path, latest_fixed,  save=True):  
    # Load the JSON 
    with open(fdr_path, 'r') as f:
        fdr_data = json.load(f)
    with open(coverage_path, 'r') as f:
        coverage_data = json.load(f)
    with open(tet_path, 'r') as f:
        tet_data = json.load(f)
    with open(fixed_line_cov_path, 'r') as f:
        flc_data = json.load(f)
    with open(latest_fixed, 'r') as f:
        lfx_data = json.load(f)
    
    merged_data = {}
    projects = {}

    ## project 이름을 통일시켜줍니다. "Time-1" => "Time_1"  
    fdr_data = _rename_keys(fdr_data)
    coverage_data = _rename_keys(coverage_data)
    tet_data = _rename_keys(tet_data)
    flc_data = _rename_keys(flc_data)
    lfx_data = _rename_keys(lfx_data)
    
    fdr_keys = set(fdr_data.keys())
    coverage_keys = set(coverage_data.keys())  
    tet_keys = set(tet_data.keys())
    flc_keys = set(flc_data.keys())
    lfx_keys = set(lfx_data.keys())
    
    ## fdr, coverage, tet 이 모두 있는 project 만 선택합니다.
    all_keys = fdr_keys.intersection(coverage_keys).intersection(tet_keys).intersection(flc_keys).intersection(lfx_keys)
    for key in all_keys:
        df1 = pd.DataFrame.from_dict(fdr_data.get(key, {}), orient='index').rename(columns={0: 'fdr'})
        df2 = pd.DataFrame.from_dict(coverage_data.get(key, {}), orient='index').rename(columns={0: 'coverage'})
        df3 = pd.DataFrame.from_dict(tet_data.get(key, {}), orient='index').rename(columns={0: 'tet'})
        df4 = pd.DataFrame.from_dict(flc_data.get(key, {}), orient='index').rename(columns={0: 'fixed_line_cov'})
        df5 = pd.DataFrame.from_dict(lfx_data.get(key, {}), orient='index').rename(columns={0: 'latest_fixed'})
        
        merged_df = pd.concat([df1, df2, df3, df4, df5], axis=1, join='inner')
        projects[key] = merged_df

        if save:  ## pkl file로 저장(data type preserve)
            output_dir = './data/merged_data'
            with open(os.path.join(output_dir, f"{key}.pkl"), 'wb') as f:
                pickle.dump(merged_df, f)
            # merged_df.to_excel(os.path.join(output_dir, f'{key}.xlsx'))
                
    return projects

if __name__ == "__main__":
    # make_all_fdr()  ## data/all_fdr.json 파일을 생성합니다.
    
    fdr_path = "./data/all_fdr.json"
    coverage_path = "./data/all_coverage.json"
    tet_path = "./data/tet.json"
    fixed_line_cov_path = "./data/coverage/fixed_line_coverage.json"
    latest_fixed_path = "./data/all_latest_fix.json"

    merge_all_data(fdr_path, coverage_path, tet_path, fixed_line_cov_path, latest_fixed_path, save=True) ## data 폴더에 merged_*.json 파일을 생성합니다.
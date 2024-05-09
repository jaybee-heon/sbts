import numpy as np
import pandas as pd
import json

# Load JSON data
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

# TODO : 두개 이상의 Pandas DataFrame 을 합치는 함수를 작성해야 함. (execution time, coverage.. 등 각각에 대한 json 파일을 합침)
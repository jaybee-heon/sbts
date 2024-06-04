import numpy as np
import pandas as pd
import json

from data_preprocess import *
from run_ga import *
import os
import pickle
import argparse

# fdr_path = "./data/all_fdr.json"
# coverage_path = "./data/all_coverage.json"
# tet_path = "./data/tet.json"
# projects =  merge_all_data(fdr_path, coverage_path, tet_path, True) 

def collect_result(fitness='cov', mutation='fdr'):
    datadir = "./data/merged_data/"
    output_path = os.path.join("./data/experiment_result/", f"f_{fitness}_m_{mutation}")

    
    for pkl_file in os.listdir(datadir):
        with open(os.path.join(datadir, pkl_file), 'rb') as f: # load pickle file for projects from merged_data
            data = pickle.load(f)
        project_name = os.path.splitext(pkl_file)[0]
        print(f'\nProject: {project_name}--------------------')

        # fitness에 사용할 metric
        match fitness:
            case 'cov':
                metric = data['coverage']
            case 'fdr':
                metric = data['fdr']

        # adequacy score에 사용할 metric
        match mutation:
            case 'fdr':
                adeq_metric = data['fdr']
            case 'flc':
                adeq_metric = data['fixed_line_cov']
            case 'cov':
                adeq_metric = data['coverage']
            case 'latest':
                adeq_metric = data['latest_fix']
                
        execution_times = data['tet']

        test_cases = np.column_stack((execution_times, metric))
        adequacy_scores = get_adequacy_scores(adeq_metric)

        bitflip_res = run_nsga(test_cases, verbose=False)
        adeq_res = run_nsga_with_adequecy(test_cases, adequacy_scores, verbose=False)

        # store Result object of pymoo
        if not os.path.exists(output_path):
            os.system(f"mkdir -p {output_path}")
        with open(os.path.join(output_path, f"{project_name}_bitflip.pkl"), 'wb') as f:
            pickle.dump(bitflip_res, f)
        with open(os.path.join(output_path, f"{project_name}_adeq.pkl"), 'wb') as f:
            pickle.dump(adeq_res, f)

if __name__ == "__main__":
    # cmd example: python experiment.py -f cov -m fdr
    parser = argparse.ArgumentParser(description="Optimize project with LLM")
    parser.add_argument("-f", dest="fitness", action="store", default='cov')
    parser.add_argument("-m", dest="mutation", action="store", default='fdr')
    args = parser.parse_args()

    collect_result(args.fitness, args.mutation)
import numpy as np
import pandas as pd
import os
import pickle
import argparse
import matplotlib.pyplot as plt

from data_preprocess import *
from run_ga import *

def min_max(data):
    return (data - np.min(data, axis=0)) / (np.ptp(data, axis=0))

def standardize(data):
    return (data - np.mean(data, axis=0)) / np.std(data, axis=0)

def get_adequacy_scores(data, scaling_method='min_max'):
    if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
        data = data.values  # Convert pandas DataFrame or Series to NumPy array
    
    if data.ndim == 1:
        data = data.reshape(-1, 1)  # Ensure data is two-dimensional if it is a single column

    match scaling_method:
        case 'min_max':
            norm = min_max(data)
        case 'std':
            norm = standardize(data)
        case _:
            print("Warning: set scaling method")
            norm = data
    
    r_norm = 1 - norm
    selection_prob = norm / np.sum(norm, axis=0)
    removal_prob = r_norm / np.sum(r_norm, axis=0)
    
    if data.shape[1] > 1:
        # Average the probabilities across all columns if more than one column
        avg_selection_prob = np.mean(selection_prob, axis=1)
        avg_removal_prob = np.mean(removal_prob, axis=1)
    else:
        # Use the probabilities directly if only one column
        avg_selection_prob = selection_prob.flatten()
        avg_removal_prob = removal_prob.flatten()
    
    adequacy_scores = np.column_stack((avg_selection_prob, avg_removal_prob))
    return adequacy_scores

def run_bitflip(data, metric, execution_times):
    test_cases = np.column_stack((execution_times, metric))
    bitflip_res, exec_times, fault_detections = run_nsga(test_cases, verbose=False)
    fault_detections_rate = fault_detections / np.max(fault_detections)
    ets, fds = [exec_times], [fault_detections_rate]
    return ets, fds, bitflip_res

def run_adequacy(data, adequacy_metric, execution_times):
    adequacy_scores = get_adequacy_scores(adequacy_metric)
    test_cases = np.column_stack((execution_times, data['coverage']))
    adeq_res, exec_times, fault_detections = run_nsga_with_adequecy(test_cases, adequacy_scores, verbose=False)
    fault_detections_rate = fault_detections / np.max(fault_detections)
    ets, fds = [exec_times], [fault_detections_rate]
    return ets, fds, adeq_res

def collect_result(fitness='cov', mutations=['fdr', 'cov']):
    datadir = "./data/merged_data/"
    all_ets_dict = {}
    all_fds_dict = {}
    all_res_dict = {}

    for pkl_file in os.listdir(datadir):
        if pkl_file.endswith('.pkl'):
            with open(os.path.join(datadir, pkl_file), 'rb') as f: # load pickle file for projects from merged_data
                data = pickle.load(f)
            project_name = os.path.splitext(pkl_file)[0]
            print(f'\nProject: {project_name}--------------------')

            # Metric to use for fitness
            match fitness:
                case 'cov':
                    metric = data['coverage']
                case 'fdr':
                    metric = data['fdr']
                # Add more cases as needed

            execution_times = data['tet']

            # Run bitflip approach 
            bitflip_ets, bitflip_fds, bitflip_res = run_bitflip(data, metric, execution_times)
            if project_name not in all_ets_dict:
                all_ets_dict[project_name] = {}
                all_fds_dict[project_name] = {}
                all_res_dict[project_name] = {}
            all_ets_dict[project_name]['bitflip'] = bitflip_ets
            all_fds_dict[project_name]['bitflip'] = bitflip_fds
            all_res_dict[project_name]['bitflip'] = bitflip_res
            print("before running adequacy", data.shape)  

            # Run adequacy approach
            for mutation in mutations:
                output_path = os.path.join("./data/experiment_result/", f"f_{fitness}_m_{mutation}")
                # Metric to use for adequacy score
                match mutation:
                    case 'fdr':
                        adeq_metric = data['fdr']
                    case 'flc':
                        adeq_metric = data['fixed_line_cov']
                    case 'cov':
                        adeq_metric = data['coverage']
                    case 'latest':
                        adeq_metric = data['latest_fixed']
                    case 'all':
                        adeq_metric = data.loc[:, ['fdr', 'fixed_line_cov', 'coverage', 'latest_fixed']]
                adequacy_ets, adequacy_fds, adeq_res = run_adequacy(data, adeq_metric, execution_times)
                print("after running adequacy", data.shape, adeq_res)  
                all_ets_dict[project_name][mutation] = adequacy_ets
                all_fds_dict[project_name][mutation] = adequacy_fds
                all_res_dict[project_name][mutation] = adeq_res

                # Save the results of each mutation
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
                with open(os.path.join(output_path, f"{project_name}_adeq.pkl"), 'wb') as f:
                    pickle.dump(all_res_dict[project_name][mutation], f)

                with open(os.path.join(output_path, f"{project_name}_bitflip.pkl"), 'wb') as f:
                    pickle.dump(bitflip_res, f)
                
    return all_ets_dict, all_fds_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize project with LLM")
    parser.add_argument("-f", "--fitness", default='cov', help="List of fitness methods to use")
    parser.add_argument("-m", "--mutations", nargs='+', default=['fdr', 'flc', 'cov', 'latest'], help="List of mutation methods to use")
    args = parser.parse_args()

    all_ets_dict, all_fds_dict = collect_result(args.fitness, args.mutations)
    for project_name in all_ets_dict:
        plot_figure(all_ets_dict[project_name], all_fds_dict[project_name], project_name, args.fitness)

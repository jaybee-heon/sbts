import numpy as np
import pandas as pd
import json

from data_preprocess import *
from run_ga import *


fdr_path = "./data/all_fdr.json"
coverage_path = "./data/all_coverage.json"
tet_path = "./data/tet.json"
projects =  merge_fdr_coverage_tet(fdr_path, coverage_path, tet_path, True) 



for key, project in projects.items(): 
    print(f'\nProject: {key}--------------------')
    fault_detections = project['fdr']
    execution_times = project['tet']
    chart_1_coverage = project['coverage']
    test = project.index

    test_cases = np.column_stack((execution_times, fault_detections))
    adequacy_scores = get_adequacy_scores(fault_detections)

    run_nsga(test_cases, verbose=False)
    run_nsga_with_adequecy(test_cases, adequacy_scores, verbose=False)
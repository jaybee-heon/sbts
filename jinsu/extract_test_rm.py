import os
import pickle
import numpy as np
import json

def split_sol():
    types = ["f_cov_m_fdr", "f_fdr_m_fdr"]
    tet_dict = {}
    for type in types:
        for target in os.listdir('../data/merged_data'):
            pid, vid = os.path.splitext(target)[0].split('_')
            print(target)

            with open(f'../data/experiment_result/{type}/{pid}_{vid}_bitflip.pkl', 'rb') as f:
                bitflip = pickle.load(f)

            with open(f'../data/experiment_result/{type}/{pid}_{vid}_adeq.pkl', 'rb') as f:
                adeq = pickle.load(f)

            with open(f'../data/merged_data/{pid}_{vid}.pkl', 'rb') as f:
                data = pickle.load(f)
            
            bitflip_tet = bitflip.F[:, 0]
            adeq_tet = adeq.F[:, 0]
            split_bitflip = (np.max(bitflip_tet) - np.min(bitflip_tet)) / 7
            split_adeq = (np.max(adeq_tet) - np.min(adeq_tet)) / 7

            bitflip_split_set = set()
            adeq_split_set = set()
            for i in range(8):
                threshold = np.min(bitflip_tet) + split_bitflip * i
                filtered_tet = bitflip_tet[bitflip_tet <= threshold]
                if filtered_tet.size > 0:
                    max_val = filtered_tet.max()
                    max_id = np.where(bitflip_tet == max_val)[0][0]
                    bitflip_split_set.add((max_id, max_val))
                

            for i in range(8):
                threshold = np.min(adeq_tet) + split_adeq * i
                filtered_tet = adeq_tet[adeq_tet <= threshold]
                if filtered_tet.size > 0:
                    max_val = filtered_tet.max()
                    max_id = np.where(adeq_tet == max_val)[0][0]
                    adeq_split_set.add((max_id, max_val))

            bitflip_dict = dict()
            adeq_dict = dict()
            for i, e in enumerate(bitflip_split_set):
                tests_to_remove = data.index[~bitflip.X[e[0]]]
                print(e[1])
                bitflip_dict[i] = {"tet": e[1], "rm_tests": list(tests_to_remove)}

            for i, e in enumerate(adeq_split_set):
                tests_to_remove = data.index[~adeq.X[e[0]]]
                adeq_dict[i] = {"tet": e[1], "rm_tests": list(tests_to_remove)}
            
            os.system(f"mkdir -p ./test_to_remove/{type}/{pid}_{vid}")
            with open(f"./test_to_remove/{type}/{pid}_{vid}/bitflip.json", "w") as f:
                json.dump(bitflip_dict, f)
            with open(f"./test_to_remove/{type}/{pid}_{vid}/adeq.json", "w") as f:
                json.dump(adeq_dict, f)

if __name__ == "__main__":
    split_sol()
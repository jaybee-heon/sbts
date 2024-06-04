import matplotlib.pyplot as plt
import numpy as np
import pickle
import pandas as pd
import os


def plot_figure_tet(tet_dict,type ):   
    labels = list(tet_dict.keys())
    men_means = []
    women_means = []
    for dict in tet_dict.values():
        print(dict)
        men_means.append(dict['adeq'])
        women_means.append(dict['bigflip'])
    print(labels, men_means, women_means)
    
    
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, men_means, width, label='adequacy')
    rects2 = ax.bar(x + width/2, women_means, width, label='bitflip')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('TET')
    ax.set_title(f'min_tet_with_failing_tests_{type}')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()



    fig.tight_layout()

    plt.savefig(f"./data/experiment_result/figure_{type}")


def plot_figure(execution_times, fault_detections, project_name):   
    # Plot the graph
    plt.figure(figsize=(10, 6))
    for idx, (execution_time, fault_detection) in enumerate(zip(execution_times, fault_detections)):
        labels = ['1/n', 'use_adequacy']
        plt.scatter(execution_time, fault_detection, label=labels[idx])

    # Add labels and title
    plt.xlabel('Execution Times')
    plt.ylabel('Fault Detections')
    plt.title('Execution Times vs Fault Detections')
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.savefig(f'figure/{project_name}_.png')  # Add missing argument

def convert_pickle_to_csv(pickle_path, csv_path):
    with open(pickle_path, 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    
if __name__ == "__main__":
    pickle_path = 'data/merged_data/Time_1.pkl'
    convert_pickle_to_csv(pickle_path, f'data/excel/{os.path.basename(pickle_path)}.csv')
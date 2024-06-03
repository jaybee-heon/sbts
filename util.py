import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import os

def plot_figure(ets_dict, fds_dict, project_name):
    """
    Plot the graph for execution times vs fault detections for a given project.
    
    ets_dict: Dictionary of execution times for each approach.
    fds_dict: Dictionary of fault detections for each approach.
    project_name: Name of the project.
    """
    colors = ['r', 'b', 'g', 'y', 'm', 'c']
    plt.figure(figsize=(10, 6))

    for idx, (approach, execution_times) in enumerate(ets_dict.items()):
        fault_detections = fds_dict[approach]
        color = colors[idx % len(colors)]
        plt.scatter(execution_times[0], fault_detections[0], label=approach, color=color)

    # Add labels and title
    plt.xlabel('Execution Times')
    plt.ylabel('Fault Detections')
    plt.title(f'Execution Times vs Fault Detections for {project_name}')
    plt.legend()
    plt.grid(True)

    # Save the plot
    if not os.path.exists('figure'):
        os.makedirs('figure')
    plt.savefig(f'figure/{project_name}_combined.png')
    plt.close()
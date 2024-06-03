import matplotlib.pyplot as plt
import numpy as np

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

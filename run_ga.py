import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.sampling.rnd import BinaryRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.mutation.am import AdequacyMutation
from pymoo.visualization.scatter import Scatter
from sklearn.preprocessing import MinMaxScaler
from util import *

# test_cases = json2PandasDf("data/tet.json")

# Define the test case prioritization problem
class TestCasePrioritizationProblem(ElementwiseProblem):
    def __init__(self, test_cases, time_budget):
        # Two objectives: minimize execution time and maximize fault detection
        self.test_cases = test_cases
        self.time_budget = time_budget
        super().__init__(n_var=len(test_cases), n_obj=2, n_constr=0, xl=np.zeros(len(test_cases)),
                         xu=np.ones(len(test_cases)))

    def _evaluate(self, x, out, *args, **kwargs):
        selected = x.astype(bool)  # Convert decision variables to boolean
        execution_times = self.test_cases[:, 0]  # Extract execution times
        fault_detections = self.test_cases[:, 1]  # Extract fault detection rates

        # Calculate the objectives
        total_execution_time = np.sum(execution_times[selected])  # Sum execution times of selected test cases
        total_fault_detection = np.sum(fault_detections[selected])  # Sum fault detections of selected test cases

        # Objectives: Minimize execution time and maximize fault detection
        out["F"] = np.array([total_execution_time, -total_fault_detection])

        # Constraint: Not to exceed the time budget
        # out["G"] = np.array([total_execution_time - self.time_budget])


# Initialize the problem
def run_nsga(test_cases, verbose=True):
    problem = TestCasePrioritizationProblem(test_cases, 5)

    # Set the algorithm configuration
    algorithm = NSGA2(
        pop_size=100,
        n_offsprings=10,
        sampling=BinaryRandomSampling(),  ## 이 후에 다른 sampling 전략(coverage 높은 순서대로)을 적용해야 함.
        crossover=SBX(prob=0.9, eta=15),
        # mutation=PM(eta=20)
        mutation=BitflipMutation(prob=1.0, prob_var=1 / len(test_cases))
    )

    # Run the optimization
    res = minimize(problem,
                   algorithm,
                   ("n_gen", 40),
                   verbose=verbose)

    # Output the results
    if verbose:
        print("Optimal Test Case Selections:")
        for i, solution in enumerate(res.X):
            print(f"Trial#{i} Test Cases Selected: {solution.astype(int)}")
            print(
                f"\tExecution Time: {np.sum(test_cases[solution.astype(bool), 0])}, Fault Detection: {np.sum(test_cases[solution.astype(bool), 1])}")
            print(f"\tTest Cases Selected: {np.sum(solution)}/{len(solution)}")
            
    #  선택된 테스트 케이스의 평균 실행 시간과 평균 Fault detection rate 를 표시 
    execution_times = list(map(lambda solution: np.sum(test_cases[solution.astype(bool), 0]), res.X))
    mean_execution_time = np.mean(execution_times)
    
    fault_detections = list(map(lambda solution: np.sum(test_cases[solution.astype(bool), 1]), res.X))
    fault_detection_rate = np.mean(fault_detections)
    
    print("\nUsing 1/N Mutation ")
    print("Mean execution Time", mean_execution_time)
    print("Mean Fault Detection Rate", fault_detection_rate)
    
    return res, execution_times, fault_detections

    
# Initialize the problem
def run_nsga_with_adequecy(test_cases, adequacy_scores, verbose=True):
    problem = TestCasePrioritizationProblem(test_cases, 5)

    # Set the algorithm configuration
    algorithm = NSGA2(
        pop_size=100,
        n_offsprings=10,
        sampling=BinaryRandomSampling(),  ## 이 후에 다른 sampling 전략(coverage 높은 순서대로)을 적용해야 함.
        crossover=SBX(prob=0.9, eta=15),
        # mutation=PM(eta=20)
        mutation=AdequacyMutation(prob=1.0, prob_var=0.3, adeq_scores=np.transpose(adequacy_scores))
    )

    # Run the optimization
    res = minimize(problem,
                   algorithm,
                   ("n_gen", 40),
                   verbose=verbose)

    # Output the results
    if verbose:
        print("Optimal Test Case Selections:")
        for i, solution in enumerate(res.X):
            print(f"Trial#{i} Test Cases Selected: {solution.astype(int)}")
            print(
                f"\tExecution Time: {np.sum(test_cases[solution.astype(bool), 0])}, Fault Detection: {np.sum(test_cases[solution.astype(bool), 1])}")
            print(f"\tTest Cases Selected: {np.sum(solution)}/{len(solution)}")
    
    
    #  선택된 테스트 케이스의 평균 실행 시간과 평균 Fault detection rate 를 표시 
    execution_times = list(map(lambda solution: np.sum(test_cases[solution.astype(bool), 0]), res.X))
    mean_execution_time = np.mean(execution_times)
    
    fault_detections = list(map(lambda solution: np.sum(test_cases[solution.astype(bool), 1]), res.X))
    fault_detection_rate = np.mean(fault_detections)
    print("\n Using Adequacy Score")
    print("Mean execution Time", mean_execution_time)
    print("Mean Fault Detection Rate", fault_detection_rate)
    
    return res, execution_times, fault_detections

def get_adequacy_scores(data, scaling_method='min_max'):
    if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
        data = data.values  # Convert pandas DataFrame or Series to NumPy array
    
    if data.ndim == 1:
        data = data.reshape(-1, 1) 
        
    match scaling_method:
        case 'min_max':
            norm = min_max(data)
        case 'std':
            norm = standardize(data)
        case _:
            print("Warning: set scaling method")
            norm = data
    r_norm = 1 - norm
    selection_prob = norm / np.sum(norm)
    removal_prob = r_norm / np.sum(r_norm)
    

    avg_selection_prob = np.mean(selection_prob, axis=1)
    avg_removal_prob = np.mean(removal_prob, axis=1)

    adequacy_scores = np.column_stack((avg_selection_prob, avg_removal_prob))
    return adequacy_scores

def min_max(data):
    print("Scaling Method: min_max")
    min_val = np.min(data)
    max_val = np.max(data)
    return (data - min_val)/(max_val - min_val)

def standardize(data):
    print("Scaling Method: std")
    mean = np.mean(data)
    std = np.std(data)
    return (data - mean) / std


if __name__ == "__main__":
    # Sample data: [execution time, fault detection rate]
    # test_cases = np.array([
    #     [0.1, 0.9],
    #     [0.4, 0.6], 
    #     [0.3, 0.8],
    #     [0.5, 0.5],
    #     [0.2, 0.7],
    #     ........
    # ])

    num_test_cases = 100

    # Generate random execution times between 0.1 and 0.5 
    execution_times = np.random.uniform(low=0.1, high=0.5, size=num_test_cases)

    # Generate random fault detection rates between 0.5 and 0.9
    fault_detections = np.random.uniform(low=0.5, high=0.9, size=num_test_cases)

    # Combine into a single array
    test_cases = np.column_stack((execution_times, fault_detections))

    # Calculate adequacy score
    adequacy_scores = get_adequacy_scores(fault_detections, scaling_method='std')

    # run_nsga(test_cases)
    run_nsga_with_adequecy(test_cases, adequacy_scores)

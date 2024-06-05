import pandas as pd

# 피클 파일 경로
file_path = './data/experiment_result/f_cov_m_fdr/Chart_1_adeq.pkl'

# 피클 파일 읽기
df = pd.read_pickle(file_path)

# 데이터프레임의 열 이름 출력
print("Columns in the dataframe:")
print(df.columns)

# 데이터프레임의 첫 몇 행 출력
print("\nFirst few rows of the dataframe:")
print(df.head())

# 각 행의 항목을 출력 (예: 처음 5개의 행)
print("\nIndividual items in the first few rows:")
for index, row in df.head().iterrows():
    print(f"Row {index}:")
    for col in df.columns:
        print(f"  {col}: {row[col]}")

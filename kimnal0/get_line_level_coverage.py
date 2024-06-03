import pandas as pd
import json
import subprocess
import os

project_file = './projects.txt'
output_file = './fixed_line_coverage.json'
all_coverage_output_file = './all_coverage.json'
test_cover = {}
all_coverage = {}

with open(project_file, 'r') as pf:
    for l in pf:
        splited_l = l.split()
        pid = splited_l[0]
        vid = splited_l[1]
        line_nums = list(map(int, splited_l[2:]))
        
        matrix_file = os.path.join('./tmp', pid+'-'+vid+'g', 'sfl/txt/matrix.txt')
        tests_file = os.path.join('./tmp', pid+'-'+vid+'g', 'sfl/txt/tests.csv')
        
        test_cover[pid+'_'+vid] = {}
        all_coverage[pid+'_'+vid] = {}

        with open(matrix_file, 'r') as mf:
            lines = mf.readlines()
            for i, line in enumerate(lines):
                lines[i] = list(map(int, line.split()[:-1]))

            print(tests_file)
            with open(tests_file, 'r') as tf:
                # tests = pd.read_csv(tf)
                tests = tf.readlines()
                for i in range(1, len(tests)):
                    test_class, test_name = tests[i].split(',')[0].split('#')
                    test_signature = test_class + "::" + test_name
                    covered_num = 0
                    for line_num in line_nums:
                        if lines[i-1][line_num-1] == 1:
                            covered_num += 1
                    test_cover[pid+'_'+vid][test_signature] = covered_num

                    total_coverage = lines[i-1].count(1)/len(lines[i-1])
                    all_coverage[pid+'_'+vid][test_signature] = total_coverage


with open(output_file, 'w') as wf:
    json.dump(test_cover, wf, indent = 4)
with open(all_coverage_output_file, 'w') as wf2:
    json.dump(all_coverage, wf2, indent = 4)
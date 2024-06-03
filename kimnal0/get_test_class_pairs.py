import os
import json

projects = os.listdir('tmp')
covered_classes_per_test = dict()
for project in projects:
    matrix_file =  os.path.join('./tmp', project, 'sfl/txt/matrix.txt')
    test_file = os.path.join('./tmp', project, 'sfl/txt/tests.csv')
    spectra_file = os.path.join('./tmp', project, 'sfl/txt/spectra.csv')

    pid, vid = project.split('-')
    vid = vid[:-1]

    covered_classes_per_test[pid+"-"+vid] = dict()

    with open(matrix_file, 'r') as mf:
        matrix = mf.readlines()
        for i, line in enumerate(matrix):
            matrix[i] = list(map(int, line.split()[:-1]))
        
        with open(test_file, 'r') as tf:
            tests = tf.readlines()

            with open(spectra_file, 'r') as sf:
                spectras = sf.readlines()

                for i in range(1, len(tests)):
                    test_class, test_name = tests[i].split(',')[0].split('#')
                    test_signature = test_class + "::" + test_name
                    covered_classes_per_test[pid+"-"+vid][test_signature] = set()
                    for j, line in enumerate(matrix[i-1]):
                        if line == 1:
                            line_name = spectras[j+1]
                            covered_class = line_name.split('#')[0].replace('$', ".")
                            covered_classes_per_test[pid+"-"+vid][test_signature].add(covered_class)
                    covered_classes_per_test[pid+'-'+vid][test_signature] = list(covered_classes_per_test[pid+'-'+vid][test_signature])

output_file = './covered_class_test_pairs.json'

with open(output_file, 'w') as wf:
    json.dump(covered_classes_per_test, wf, indent = 4)




        
        


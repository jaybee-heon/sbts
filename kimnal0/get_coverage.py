import subprocess
import json
import xml.etree.ElementTree as ET

# 명령어를 실행하는 함수
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)

def make_info_command(pid):
    info_pre = "defects4j info -p "+pid
    return info_pre

def make_checkout_command(pid, vid):
    command = "defects4j checkout -p "+pid+" -v "+vid+"f -w ./checkout/"+pid+"_"+vid
    return command

def make_compile_command(pid, vid):
    command = "defects4j compile -w checkout/"+pid+"_"+vid
    return command

def make_test_command(pid, vid):
    command = "defects4j test -w checkout/"+pid+"_"+vid
    return command

def make_coverage_command(pid, vid, test_signature):
    command = "defects4j coverage -w checkout/"+pid+"_"+vid+" -t "+test_signature
    return command

if __name__ == "__main__":
    projects = "./projects.txt"
    output_file = './coverage.json'
    coverage = dict()
    with open(projects) as pf:
        for line in pf:
            pid, vid = line.split()
            coverage[pid+"_"+vid] = dict()

            print(f"Doing checkout...")
            print(f"{pid}-{vid}")
            run_command(make_checkout_command(pid, vid))

            print("Compiling...")
            run_command(make_compile_command(pid, vid))

            print(f"Testing...: {pid}-{vid}")
            run_command(make_test_command(pid, vid))

            test_file_path = "./checkout/"+pid+"_"+vid+"/all_tests"
            with open(test_file_path) as tf:
                all_tests = tf.readlines()
            
            for test in all_tests:
                test_method, test_class = test.split('(')
                test_class = test_class[:-2]
                test_signature = test_class+"::"+test_method
                coverage[pid+"_"+vid][test_signature] = dict()

                print("Measuring coverage...")
                print(test_signature)
                run_command(make_coverage_command(pid, vid, test_signature))
                
                coverage_file = './checkout/'+pid+"_"+vid+"/coverage.xml"

                tree = ET.parse(coverage_file)
                root = tree.getroot()

                line_rate = root.get('line-rate')
                branch_rate = root.get('branch-rate')

                coverage[pid+"_"+vid][test_signature]={"line_rate": line_rate, "branch_rate": branch_rate}


    
    with open(output_file, 'w') as wf:
        json.dump(coverage, wf, indent = 4)







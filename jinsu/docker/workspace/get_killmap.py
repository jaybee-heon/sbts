# from get_coverage import *
import argparse
import csv
import os
from tqdm import tqdm
import json
import time


def make_fdr_command(pid, vid, test_signature):
    command = f"defects4j mutation -w checkout/{pid}_{vid} -t {test_signature} -i all_classes/{pid}-{vid}/all_classes"
    return command

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="파일을 지정된 부분 수로 나누는 스크립트")
    parser.add_argument('project', type=str, help='project id')
    parser.add_argument('version', type=int, help='version id')
    parser.add_argument('part_idx', type=int, help='partition id')

    args = parser.parse_args()

    fdr_result = dict()

    pid = args.project
    vid = args.version
    vid = str(vid)
    tmp_dir = f"/tmp/{pid}-{vid}f"
    output_dir = "./fdr"
    output_file = f"./fdr/{pid}-{vid}_fdr.json"
    fdr_result[pid + "_" + vid] = dict()

    if not os.path.exists(output_dir):
        os.system(f"mkdir -p {output_dir}")

    print(f"Doing checkout...")
    print(f"{pid}-{vid}")
    # run_command(make_checkout_command(pid, vid))
    os.system(f"defects4j checkout -p {pid} -v {vid}f -w {tmp_dir}")
    os.system(f"cd {tmp_dir} && defects4j test")

    # print("Compiling...")
    # run_command(make_compile_command(pid, vid))

    # print(f"Testing...: {pid}-{vid}")
    # run_command(make_test_command(pid, vid))

    test_file_path = "./checkout/" + pid + "_" + vid + "/all_tests"
    # with open(f"/root/workspace/all_classes/{pid}-{vid}/all_tests", 'r') as tf:
    with open(os.path.join(tmp_dir, "all_tests"), 'r') as tf:
        all_tests = tf.readlines()
    num_parts = 4
    part_idx = args.part_idx
    print(f"{part_idx + 1}/{num_parts} is running")
    num_tests = len(all_tests)
    part_size = num_tests // num_parts
    remainder = num_tests % num_parts

    start = part_idx * part_size
    end = start + part_size + (remainder if part_idx + 1 == num_parts else 0)
    test_partition = all_tests[start:end]

    for test in tqdm(test_partition):
        test_method, test_class = test.split('(')
        test_class = test_class[:-2]
        test_signature = test_class+"::"+test_method
        
        fdr_result[pid+"_"+vid][test_signature] = []

        if os.path.exists(output_file):
            with open(output_file, 'r') as rf:
                fdr_result = json.load(rf)
                if test_signature in fdr_result[pid+"_"+vid]:
                    continue

        

        # fault? bug?
        print("Measuring Bug Detection Rate...")
        print(test_signature)

        # os.system(f"cd {tmp_dir} && defects4j mutation -t {test_signature}")
        os.system(f"cd {tmp_dir} && defects4j mutation -t {test_signature} -i /root/workspace/all_classes/{pid}-{vid}/all_classes")
        with open(os.path.join(tmp_dir, "kill.csv"), "r") as f:
            rdr = csv.reader(f)

            for line in rdr:
                if line[0] == "MutantNo":
                    continue
                if line[1] == "LIVE":
                    continue
                fdr_result[pid+"_"+vid][test_signature].append(line[0])
        # print(fdr_result)
        # break
        with open(output_file, 'w') as wf:
            json.dump(fdr_result, wf, indent=4)

        # os.system(f"cd {tmp_dir} && defects4j mutation -t {test_signature} -i /root/workspace/all_classes/{pid}-{vid}/all_classes > /root/workspace/error.txt")


        # skip errorneous tests
        # with open("/root/workspace/error.txt", 'r') as f:
        #     stdout = f.read()
        #     if "BUILD FAILED" in stdout:
        #         continue
        # os.system("rm -rf /root/workspace/error.txt")

        # analysis_result = './checkout/' + pid + "_" + vid + "/summary.csv"
        # with open(os.path.join(tmp_dir, "summary.csv"), newline='') as file:
        #     reader = csv.reader(file)
        #     next(reader)
        #     result = next(reader)
        #     mutants_generated = int(result[0])
        #     mutants_covered = int(result[1])
        #     mutants_killed = int(result[2])
        #     mutants_live = int(result[3])
        #     fdr_result[pid + "_" + vid][test_signature] = {"mutants-generated": mutants_generated,
        #                                                    "mutants-covered": mutants_covered,
        #                                                    "mutants-killed": mutants_killed,
        #                                                    "mutants-live": mutants_live,
        #                                                    "mutation-score": mutants_killed/mutants_generated}


        time.sleep(0.3)
        # break
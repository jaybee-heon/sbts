import os
import pickle
import json
import lizard

def solution_mutation():
    types = ["f_cov_m_fdr", "f_fdr_m_fdr"]
    tet_dict = {}
    for type in types:
        datadir = f"./test_to_remove/{type}"
        for target in os.listdir(datadir):
            pid, vid = target.split('_')
            print(pid, vid)
            tmp_dir = f"/tmp/{pid}-{vid}f"
            
            os.system(f"rm -rf {tmp_dir}")
            os.system(f"defects4j checkout -p {pid} -v {vid}f -w {tmp_dir}")

            if not os.path.exists(os.path.join(tmp_dir, "dir.src.tests")):
                os.system(f"cd {tmp_dir} && defects4j export -p dir.src.tests -o dir.src.tests")
            with open(os.path.join(tmp_dir, "dir.src.tests"), 'r') as f:
                dir_src_tests = f.read()

            with open(os.path.join(datadir, f"{target}/bitflip.json"), "r") as f:
                bitflip = json.load(f)

            with open(os.path.join(datadir, f"{target}/adeq.json"), "r") as f:
                adeq = json.load(f)

            for id, split in bitflip.items():
                for test in split['rm_tests']:
                    test_path, test_name = test.split('::')
                    test_path = test_path.replace('.', '/') + ".java"
                    # print(test_path, test_name)
                    # os.system(f"cd {tmp_dir} && lizard {os.path.join(dir_src_tests, test_path)}")
                    a_f = lizard.analyze_file(os.path.join(tmp_dir, os.path.join(dir_src_tests, test_path)))
                    # print(dir(a_f))
                    # print(a_f.function_list[0].start_line, a_f.function_list[0].end_line)
                    start = a_f.function_list[0].start_line
                    end = a_f.function_list[0].end_line
                    with open(os.path.join(tmp_dir, os.path.join(dir_src_tests, test_path)), "r") as f:
                        code = f.readlines()
                    mod_code = code[:start-1] + code[end:]
                    with open(os.path.join(tmp_dir, os.path.join(dir_src_tests, test_path)), "w") as f:
                        f.write(''.join(mod_code))
                os.system(f"cd {tmp_dir} && defects4j mutation")
                break
            break
        break

    return

if __name__ == "__main__":
    solution_mutation()
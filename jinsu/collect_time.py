import os
import pickle
import re
import json

def analyze_file(path):
    result = dict()
    with open(path, "r") as f:
        for line in f.readlines():
            ts = re.match("Testsuite: (.*)", line)
            tc = re.match("Testcase: (.*) took (.*) sec", line)
            if not ts is None:
                testsuite = ts.group(1)
                continue
            if not tc is None:
                name = tc.group(1)
                time = tc.group(2)
                
                tid = testsuite + "::" + name
                result[tid] = float(time)
                continue
    return result

if __name__ == "__main__":
    with open("newest.pkl", "rb") as f:
        data = pickle.load(f)
        print(data)

    time_data = dict()
    for pid, vid in data.items():
        tmp_dir = f"/tmp/{pid}-{vid}f"
        time_data[f"{pid}-{vid}"] = dict()


        if not os.path.exists(tmp_dir):
            os.system(f"defects4j checkout -p {pid} -v {vid}f -w {tmp_dir}")
        if not os.path.exists(os.path.join(tmp_dir, "TEST-*")):
            os.system(f"cd {tmp_dir} && defects4j test")

        for file in os.listdir(tmp_dir):
            if not file.startswith("TEST-"):
                continue
            result = analyze_file(os.path.join(tmp_dir, file))
            time_data[f"{pid}-{vid}"].update(result)

    with open("tet.json", "w") as f:
        json.dump(time_data, f, indent=" ")
import os
import argparse
import pickle



if __name__ == "__main__":  
  with open("newest.pkl", "rb") as f:
    data = pickle.load(f)
    print(data)

  for pid, vid in data.items():
    if not os.path.exists(f"./all_classes/{pid}-{vid}"):
      os.system(f"mkdir ./all_classes/{pid}-{vid}")
    tmp_dir = f"/tmp/{pid}-{vid}f"
    
    if not os.path.exists(tmp_dir):
      os.system(f"defects4j checkout -p {pid} -v {vid}f -w {tmp_dir}")
    os.system(f"cd {tmp_dir} && defects4j export -p dir.bin.classes -o dir.bin.classes")
    with open(os.path.join(tmp_dir, "dir.bin.classes"), 'r') as f:
      dir_bin_classes = f.read()

    target_dir = os.path.join(tmp_dir, dir_bin_classes)

    with open(f"./all_classes/{pid}-{vid}/all_classes", 'w') as output_file:
      for root, subdirs, files in os.walk(target_dir):
        package = os.path.relpath(root, target_dir).replace('/', '.')
        for f in files:
          if f[-6:] == '.class':
            classname = f[:-6]
            output_file.write(package + '.' + classname + '\n')
    # break
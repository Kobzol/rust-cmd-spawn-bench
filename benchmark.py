import os
import subprocess
import sys
import time

for key in list(os.environ.keys()):
    if key != "PATH":
        del os.environ[key]

name = sys.argv[1]

counts = [1000, 5000, 10000, 25000]
repeat_count = 3

print("name,process_count,env_count,mode,allocated,duration")

processes = []
for process_count in counts:
    for _ in range(repeat_count):
        processes.clear()

        start = time.time()
        for _ in range(process_count):
            p = subprocess.Popen(["sleep", "0"])
            processes.append(p)
        duration = time.time() - start

        print(f"{name}-py,{process_count},1,spawn,0,{duration}")

        for p in processes:
            p.wait()

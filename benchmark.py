import subprocess
import time

for _ in range(100):
    start = time.time()
    subprocess.run(["sleep", "0"])
    print(time.time() - start)

import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

files = sys.argv[1:]
data = pd.concat(tuple(pd.read_csv(f) for f in files))


def plot_spawn(data: pd.DataFrame):
    data = data.copy()
    data = data[data["mode"] == "spawn"]

    def plot_fn(data, **kwargs):
        sns.lineplot(data=data, x="process_count", y="duration", hue="name")

    plot_fn(data)


plot_spawn(data)

os.makedirs("charts", exist_ok=True)
plt.savefig("charts/spawn-count.png")

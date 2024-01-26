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
        ax = sns.lineplot(data=data, x="process_count", y="duration", hue="name")
        ax.set(xlabel="Process count", ylabel="Duration [s]", ylim=(0, None))
        ax.legend_.set_title(None)
        sns.move_legend(ax, "upper left")

    plot_fn(data)
    plt.savefig("charts/spawn-count.png")


def plot_mem(data: pd.DataFrame):
    data = data.copy()
    data = data[data["mode"] == "spawn"]
    data["allocated"] /= 1024 * 1024

    def plot_fn(data, **kwargs):
        ax = sns.lineplot(data=data, x="allocated", y="duration", hue="name")
        ax.set(xlabel="RSS [MiB}", ylabel="Duration [s]", ylim=(0, None))
        ax.legend_.set_title(None)
        sns.move_legend(ax, "upper left")

    plot_fn(data)
    plt.savefig("charts/spawn-mem.png")


os.makedirs("charts", exist_ok=True)

with plt.xkcd():
    plot_spawn(data)
    # plot_mem(data)

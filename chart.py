import os
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def load_data(files: List[str]) -> pd.DataFrame:
    data = pd.concat(tuple(pd.read_csv(f) for f in files))

    def rename(name: str) -> str:
        if "-" not in name:
            return f"{name}-rust"
        return name

    data["name"] = data["name"].apply(rename)
    return data


def plot_spawn_rust_local_cluster():
    data = load_data(["karolina.csv", "local.csv"])

    data = data[data["mode"] == "spawn"]

    def plot_fn(data, **kwargs):
        ax = sns.lineplot(data=data, x="process_count", y="duration", hue="name")
        ax.set(xlabel="Process count", ylabel="Duration [s]", ylim=(0, None))
        ax.legend_.set_title(None)
        sns.move_legend(ax, "upper left")

    plot_fn(data)
    plt.savefig("charts/spawn-rust-local-vs-cluster.png")


# def plot_mem():
#     data = pd.concat(tuple(pd.read_csv(f) for f in files))
#     data = data[data["mode"] == "spawn"]
#     data["allocated"] /= 1024 * 1024
#
#     def plot_fn(data, **kwargs):
#         ax = sns.lineplot(data=data, x="allocated", y="duration", hue="name")
#         ax.set(xlabel="RSS [MiB}", ylabel="Duration [s]", ylim=(0, None))
#         ax.legend_.set_title(None)
#         sns.move_legend(ax, "upper left")
#
#     plot_fn(data)
#     plt.savefig("charts/spawn-mem.png")


os.makedirs("charts", exist_ok=True)

plot_spawn_rust_local_cluster()
# plot_mem()

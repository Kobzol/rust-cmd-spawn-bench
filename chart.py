import os
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def load_data(files: List[str], normalize=True) -> pd.DataFrame:
    data = pd.concat(tuple(pd.read_csv(Path("data") / f) for f in files))

    def rename(name: str) -> str:
        if "-" not in name:
            return f"{name}-rust"
        return name

    if normalize:
        data["name"] = data["name"].apply(rename)
    return data


def plot_spawn_rust_local_cluster():
    data = load_data(["karolina.csv", "local.csv"], normalize=False)

    data = data[data["mode"] == "spawn"]

    def plot_fn(data, **kwargs):
        ax = sns.barplot(data=data, x="process_count", y="duration", hue="name", errorbar=None)
        ax.set(xlabel="Process count", ylabel="Duration [s]", ylim=(0, None))
        ax.legend_.set_title(None)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f")
        sns.move_legend(ax, "upper left")

    plt.cla()
    plot_fn(data)
    plt.savefig("charts/spawn-rust-local-vs-cluster.png")


VFORK_HUE_ORDER = ("cluster-fork", "cluster-vfork", "local-fork", "local-vfork")


def plot_vfork_cpp_local_cluster():
    data = load_data(["karolina-fork-1.csv", "karolina-fork-2.csv", "local-fork-1.csv", "local-fork-2.csv"])

    assert set(data["allocated"]) == {0}
    data = data[data["mode"] == "spawn"]

    def rename(row):
        row = row.copy()
        if row["vfork"] == 1:
            row["name"] = row["name"].replace("fork", "vfork")
        row["name"] = row["name"].replace("-cpp", "")
        return row

    data = data.apply(rename, axis=1)

    def plot_fn(data, **kwargs):
        ax = sns.barplot(data=data, x="process_count", y="duration", hue="name",
                         hue_order=VFORK_HUE_ORDER, errorbar=None)
        ax.set(xlabel="Process count", ylabel="Duration [s]", ylim=(0, 4))
        ax.legend_.set_title(None)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", rotation=90, padding=5)
        sns.move_legend(ax, "upper left")

    plt.cla()
    plot_fn(data)
    plt.savefig("charts/spawn-vfork-cpp-local-vs-cluster.png")


def plot_vfork_cpp_memory_local_cluster():
    items = []
    for i in range(1, 5):
        for name in ("karolina", "local"):
            items.append(f"{name}-fork-{i}.csv")
    data = load_data(items)

    data = data[data["mode"] == "spawn"]
    data = data[data["process_count"] == 10000]
    data["allocated"] /= 1024 * 1024

    def rename(row):
        row = row.copy()
        if row["vfork"] == 1:
            row["name"] = row["name"].replace("fork", "vfork")
        row["name"] = row["name"].replace("-cpp", "")
        return row

    data = data.apply(rename, axis=1)

    def plot_fn(data, **kwargs):
        ax = sns.barplot(data=data, x="allocated", y="duration", hue="name",
                         hue_order=VFORK_HUE_ORDER, errorbar=None)
        ax.set(xlabel="RSS [MiB]", ylabel="Duration [s]", ylim=(0, 30))
        ax.legend_.set_title(None)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", rotation=90, padding=5)
        sns.move_legend(ax, "upper left")

    plt.cla()
    plot_fn(data)
    plt.savefig("charts/spawn-vfork-cpp-memory-local-vs-cluster.png")


def plot_vfork_py_local_cluster():
    data = load_data(["karolina-py.csv", "local-py.csv"])
    data = data[data["mode"] == "spawn"]

    def plot_fn(data, **kwargs):
        ax = sns.barplot(data=data, x="process_count", y="duration", hue="name", errorbar=None)
        ax.set(xlabel="Process count", ylabel="Duration [s]", ylim=(0, 30))
        ax.legend_.set_title(None)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", rotation=90, padding=5)
        sns.move_legend(ax, "upper left")

    plt.cla()
    plot_fn(data)
    plt.savefig("charts/spawn-vfork-py-local-vs-cluster.png")


def plot_sleep_vs_usr_bin_sleep():
    data = load_data(["local-sleep.csv", "local-usr-bin-sleep.csv"])
    data = data[data["mode"] == "spawn"]

    def plot_fn(data, **kwargs):
        ax = sns.barplot(data=data, x="process_count", y="duration", hue="name", errorbar=None)
        ax.set(xlabel="Process count", ylabel="Duration [s]", ylim=(0, 3))
        ax.legend_.set_title(None)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", rotation=90, padding=5)
        sns.move_legend(ax, "upper left")

    plt.cla()
    plot_fn(data)
    plt.savefig("charts/spawn-sleep-vs-usr-bin-sleep.png")


# def plot_mem():
#     data = pd.concat(tuple(pd.read_csv(f) for f in files))
#     data = data[data["mode"] == "spawn"]
#     data["allocated"] /= 1024 * 1024
#
#     def plot_fn(data, **kwargs):
#         ax = sns.lineplot(data=data, x="allocated", y="duration", hue="name")
#         ax.set(xlabel="RSS [MiB]", ylabel="Duration [s]", ylim=(0, None))
#         ax.legend_.set_title(None)
#         sns.move_legend(ax, "upper left")
#
#     plot_fn(data)
#     plt.savefig("charts/spawn-mem.png")


os.makedirs("charts", exist_ok=True)

# plot_spawn_rust_local_cluster()
# plot_vfork_cpp_local_cluster()
# plot_vfork_cpp_memory_local_cluster()
# plot_vfork_py_local_cluster()
plot_sleep_vs_usr_bin_sleep()
# plot_mem()

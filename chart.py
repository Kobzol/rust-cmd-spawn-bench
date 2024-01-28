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


def plot_env_noset_local_cluster():
    data = load_data(["local-env-noset.csv", "karolina-env-noset.csv"])
    data = data[data["mode"] == "spawn"]
    data["env_count"] -= 1  # Ignore PATH

    def rename(name: str) -> str:
        return name[:name.index("-")]

    data["name"] = data["name"].apply(rename)

    palette = sns.color_palette()
    palette = [palette[0], palette[2]]

    def plot_fn(data, **kwargs):
        ax = sns.barplot(data=data, x="env_count", y="duration", hue="name", errorbar=None,
                         palette=palette)
        ax.set(xlabel="Environment variable count", ylabel="Duration [s]", ylim=(0, 14))
        ax.legend_.set_title(None)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", rotation=90, padding=5)
        sns.move_legend(ax, "upper left")

    plt.cla()
    plot_fn(data)
    plt.savefig("charts/spawn-env-noset-local-vs-cluster.png")


def plot_env_local_cluster():
    data = load_data(["local-env-noset.csv", "local-env-set.csv", "karolina-env-noset.csv", "karolina-env-set.csv"])
    data = data[data["mode"] == "spawn"]
    data["env_count"] -= 1  # Ignore PATH

    def plot_fn(data, **kwargs):
        ax = sns.barplot(data=data, x="env_count", y="duration", hue="name", errorbar=None)
        ax.set(xlabel="Environment variable count", ylabel="Duration [s]", ylim=(0, 14))
        ax.legend_.set_title(None)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", rotation=90, padding=5)
        sns.move_legend(ax, "upper left")

    plt.cla()
    plot_fn(data)
    plt.savefig("charts/spawn-env-local-vs-cluster.png")


def plot_env_opt_local_cluster():
    data = load_data(["local-base.csv", "local-opt.csv"])
    data = data[data["mode"] == "spawn"]
    data["env_count"] -= 1  # Ignore PATH
    # data = data.groupby(["name", "env_count"]).min().reset_index()

    def plot_fn(data, **kwargs):
        ax = sns.barplot(data=data, x="env_count", y="duration", hue="name", errorbar=None)
        ax.set(xlabel="Environment variable count", ylabel="Duration [s]", ylim=(0, 3))
        ax.legend_.set_title(None)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", rotation=90, padding=5)
        sns.move_legend(ax, "upper left")

    plt.cla()
    plot_fn(data)
    plt.savefig("charts/spawn-env-opt-local.png")


def plot_async_local_cluster(ext=""):
    items = []
    for mode in ("single", "single-blocking", "multi-2", "multi-4", "multi-8"):
        for name in ("karolina", "local"):
            items.append(f"{name}-{ext}{mode}.csv")
    data = load_data(items)

    def combine(row):
        mode = f"{row['mode'].lower()}"
        thread_count = row["thread_count"]
        if thread_count > 1:
            mode += f"-{thread_count}"
        return mode

    data["mode"] = data[["mode", "thread_count"]].apply(combine, axis=1)
    data["name"] = data["name"].apply(lambda name: name[:name.index("-")])

    def plot_fn(data, **kwargs):
        ax = sns.barplot(data=data, x="mode", y="duration", hue="name", errorbar=None)
        ax.set(xlabel="Mode", ylabel="Duration [s]", ylim=(0, 50))
        ax.legend_.set_title(None)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", rotation=90, padding=5)

    plt.cla()
    plot_fn(data)
    plt.savefig(f"charts/spawn-async-{ext}local-vs-cluster.png")


os.makedirs("charts", exist_ok=True)

# plot_spawn_rust_local_cluster()
# plot_vfork_cpp_local_cluster()
# plot_vfork_cpp_memory_local_cluster()
# plot_vfork_py_local_cluster()
# plot_sleep_vs_usr_bin_sleep()
# plot_env_noset_local_cluster()
# plot_env_local_cluster()
# plot_env_opt_local_cluster()
plot_async_local_cluster()
plot_async_local_cluster("noenv-")

# -*- coding: utf-8 -*-
"""
Plot the metrics in additive order of all strategies on the tested graph, chosing the medoid in AUC of Coverage and Directness as the shown trial.
"""

import os
import json
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt


FOLDER_DATA = "./data/processed/"
FOLDER_PLOT = "./plots/"
RAND_TRIAL_NUMBER = 500
BUFF_SIZE = 400
TIMESTAMPS = [
    "2021-01-01",
    "2023-05-17",
    "2023-10-01",
    "2024-01-15",
    "2024-04-04",
    "2024-08-22",
    "2024-12-22",
    "2025-06-02",
    "2026-01-28",
    "No",
]


def main():
    with open("./scripts/I_plot_lineplot.json", "r") as f:
        plot_params = json.load(f)
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    folderplot = FOLDER_PLOT + "lineplot/"
    if not os.path.exists(folderplot):
        os.makedirs(folderplot)
    avg = {}
    for met in plot_params["order"]:
        foldermet = FOLDER_DATA + f"bs_{BUFF_SIZE}_{met}/"
        if met == "random":
            df_concat = pd.DataFrame()
            for i in range(RAND_TRIAL_NUMBER):
                df = pd.read_json(foldermet + f"random_{i:03}/metrics_growth.json")
                df_concat = pd.concat([df_concat, df])
            df_avg = pd.DataFrame(average_x(df_concat))
        else:
            df_avg = pd.read_json(foldermet + "metrics_growth.json")
        avg[met] = df_avg
    for met_plot, met_label in {
        "coverage": "Coverage ($km^2$)",
        "directness": "Directness",
        "num_cc": "Number of components",
        "length_lcc": "Length of LCC (km)",
    }.items():
        fig, ax = plt.subplots(figsize=plot_params["figsize"])
        if met_plot == "coverage":
            ratio = 10**6
        elif met_plot == "length_lcc":
            ratio = 10**3
        else:
            ratio = 1
        ax.set_ylabel(met_label)
        for ids, met in enumerate(plot_params["order"]):
            df = avg[met]
            ax.plot(
                df["xx"] / 10**3,
                df[met_plot] / ratio,
                **{
                    key: val[ids]
                    for key, val in plot_params.items()
                    if key not in ["dpi", "figsize", "rcparams", "order"]
                },
            )
        ax.set_xlabel("Built length ($km$)")
        ax.set_axisbelow(True)
        fig.tight_layout()
        ax.legend()
        fig.savefig(folderplot + f"/{met_plot}.png")
        plt.close(fig=fig)


def average_x(df):
    arr = []
    for ind in set(df.index):
        arr.append(df[df.index == ind].mean())
    return arr


if __name__ == "__main__":
    main()

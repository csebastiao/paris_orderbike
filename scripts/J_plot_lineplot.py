# -*- coding: utf-8 -*-
"""
Plot the metrics in additive order of all strategies on Paris bikenet, showing the average in AUC of Coverage and Directness for multiple trials.
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
from G_grow_bikenet import (
    BUFF_SIZE,
    NUM_HIER_TRIAL,
    NUM_RAND_TRIAL,
    NUM_COV_TRIAL,
    FOLDEROOT,
)
from I_grow_random_real_bikenet import NUM_RAND_REAL_TRIAL

MARKERDIST = 0.1
MARKERSIZE = 10
LINEWIDTH = 2
FOLDERPLOT = "./plots/"
MET_PLOT = {
    "coverage": "Coverage ($km^2$)",
    "directness": "Directness",
    "num_cc": "Number of components",
    "length_lcc": "Length of LCC (km)",
}


def main():
    with open("./scripts/J_plot_lineplot.json", "r") as f:
        plot_params = json.load(f)
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    for end_folder in [
        "Nothing",
        "2021",
        "2026",
    ]:
        folder_data = FOLDEROOT + end_folder + "/"
        folder_plot = FOLDERPLOT + end_folder + "/lineplot/"
        if not os.path.exists(folder_plot):
            os.makedirs(folder_plot)
        avg = {}
        df_concat = pd.DataFrame()
        for i in range(NUM_RAND_TRIAL):
            df = pd.read_json(
                folder_data + f"bs_{BUFF_SIZE}_random/random_{i:03}/metrics_growth.json"
            )
            df_concat = pd.concat([df_concat, df])
        random_df = pd.DataFrame(average_x(df_concat))
        for met in plot_params["order"]:
            foldermet = folder_data + f"bs_{BUFF_SIZE}_{met}/"
            if met in [
                "road_hierarchy",
                "bikenet_hierarchy",
                "coverage",
                "real_random",
            ]:
                df_concat = pd.DataFrame()
                if met in ["road_hierarchy", "bikenet_hierarchy"]:
                    num_step = NUM_HIER_TRIAL
                elif met in ["coverage"]:
                    num_step = NUM_COV_TRIAL
                elif met in ["real_random"]:
                    num_step = NUM_RAND_REAL_TRIAL
                for i in range(num_step):
                    df = pd.read_json(foldermet + f"{met}_{i:03}/metrics_growth.json")
                    df_concat = pd.concat([df_concat, df])
                df_avg = pd.DataFrame(average_x(df_concat))
            else:
                df_avg = pd.read_json(foldermet + "metrics_growth.json")
            avg[met] = df_avg
        for normalized in [True, False]:
            for met_plot, met_label in MET_PLOT.items():
                fig, ax = plt.subplots(figsize=plot_params["figsize"])
                if met_plot == "coverage":
                    ratio = 10**6
                elif met_plot == "length_lcc":
                    ratio = 10**3
                else:
                    ratio = 1
                if normalized:
                    ax.set_ylabel(met_label + ", normalized")
                else:
                    ax.set_ylabel(met_label)
                for ids, met in enumerate(plot_params["order"]):
                    df = avg[met]
                    if met == "real":
                        markevery = 1
                        zorder = 4
                    elif met == "real_random":
                        markevery = 0
                        zorder = 2
                    else:
                        markevery = MARKERDIST
                        zorder = 3
                    if normalized:
                        val_df_normalize = [0]
                        for idx, target_x in enumerate(df["xx"][1:-1]):
                            if target_x in random_df["xx"]:
                                val_df_normalize.append(
                                    random_df[met_plot][
                                        list(random_df["xx"].index(target_x))
                                    ]
                                )
                            else:
                                abo_x = random_df["xx"][
                                    random_df["xx"] > target_x
                                ].min()
                                abo_v = random_df[met_plot][
                                    list(random_df["xx"]).index(abo_x)
                                ]
                                bel_x = random_df["xx"][
                                    random_df["xx"] < target_x
                                ].max()
                                bel_v = random_df[met_plot][
                                    list(random_df["xx"]).index(bel_x)
                                ]
                                val_df_normalize.append(
                                    df[met_plot][idx + 1]
                                    - (
                                        bel_v
                                        + (target_x - bel_x)
                                        * (abo_v - bel_v)
                                        / (abo_x - bel_x)
                                    )
                                )
                        val_df_normalize.append(0)
                        ax.plot(
                            df["xx"] / 10**3,
                            np.array(val_df_normalize) / ratio,
                            markevery=markevery,
                            markersize=MARKERSIZE,
                            linewidth=LINEWIDTH,
                            zorder=zorder,
                            **{
                                key: val[ids]
                                for key, val in plot_params.items()
                                if key not in ["dpi", "figsize", "rcparams", "order"]
                            },
                        )
                    else:
                        ax.plot(
                            df["xx"] / 10**3,
                            df[met_plot] / ratio,
                            markevery=markevery,
                            markersize=MARKERSIZE,
                            linewidth=LINEWIDTH,
                            zorder=zorder,
                            **{
                                key: val[ids]
                                for key, val in plot_params.items()
                                if key not in ["dpi", "figsize", "rcparams", "order"]
                            },
                        )
                xlims = ax.get_xlim()
                if normalized:
                    ax.plot(
                        xlims,
                        [0, 0],
                        color="lightgrey",
                        zorder=1,
                    )
                else:
                    ax.plot(
                        random_df["xx"] / 10**3,
                        random_df[met_plot] / ratio,
                        markevery=MARKERDIST,
                        markersize=MARKERSIZE,
                        linewidth=LINEWIDTH,
                        marker="o",
                        color="grey",
                        label="Random",
                        zorder=2,
                    )
                ax.set_xlim(xlims)
                ax.set_xlabel("Built length ($km$)")
                ax.set_axisbelow(True)
                fig.tight_layout()
                ax.legend()
                filename = folder_plot + f"/{met_plot}"
                if normalized:
                    filename += "_normalized"
                fig.savefig(filename + ".png")
                plt.close(fig=fig)


def average_x(df):
    arr = []
    for ind in set(df.index):
        arr.append(df[df.index == ind].mean())
    return arr


if __name__ == "__main__":
    main()

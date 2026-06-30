# -*- coding: utf-8 -*-
"""
Plot the hedgehog plot for selected growth strategies.
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
from G_grow_bikenet import (
    BUFF_SIZE,
    NUM_RAND_TRIAL,
    FOLDEROOT,
    END_FOLDERS,
)
from I_plot_lineplot import (
    FOLDERPLOT,
    MARKERDIST,
    MARKERSIZE,
    LINEWIDTH,
    MET_PLOT,
    average_x,
)


def main():
    with open("./scripts/J_plot_hedgehog.json", "r") as f:
        plot_params = json.load(f)
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    folder_plot = FOLDERPLOT + "/hedgehog/"
    if not os.path.exists(folder_plot):
        os.makedirs(folder_plot)
    # Get random values to normalize
    df_concat = pd.DataFrame()
    for i in range(NUM_RAND_TRIAL):
        df = pd.read_json(
            FOLDEROOT
            + f"Nothing/bs_{BUFF_SIZE}_random/random_{i:03}/metrics_growth.json"
        )
        df_concat = pd.concat([df_concat, df])
    random_df = pd.DataFrame(average_x(df_concat))
    # Get real values and normalize them
    df_real = pd.read_json(
        FOLDEROOT + f"Nothing/bs_{BUFF_SIZE}_real/metrics_growth.json"
    )
    dict_real_normalized = {}
    for met in MET_PLOT.keys():
        val_real_normalized = [0]
        for idx, target_x in enumerate(df_real["xx"][1:-1]):
            if target_x in random_df["xx"]:
                val_real_normalized.append(
                    random_df[met][list(random_df["xx"].index(target_x))]
                )
            else:
                abo_x = random_df["xx"][random_df["xx"] > target_x].min()
                abo_v = random_df[met][list(random_df["xx"]).index(abo_x)]
                bel_x = random_df["xx"][random_df["xx"] < target_x].max()
                bel_v = random_df[met][list(random_df["xx"]).index(bel_x)]
                val_real_normalized.append(
                    df_real[met][idx + 1]
                    - (bel_v + (target_x - bel_x) * (abo_v - bel_v) / (abo_x - bel_x))
                )
        val_real_normalized.append(0)
        dict_real_normalized[met] = val_real_normalized
    for ids, met in enumerate(plot_params["order"]):
        for normalized in [True, False]:
            for met_plot, met_label in MET_PLOT.items():
                fig, ax = plt.subplots(figsize=plot_params["figsize"])
                if met_plot == "coverage":
                    ratio = 10**6
                elif met_plot == "length_lcc":
                    ratio = 10**3
                else:
                    ratio = 1
                ax.set_ylabel(met_label)
                # Add real growth
                if normalized:
                    ax.plot(
                        df_real["xx"] / 10**3,
                        np.array(dict_real_normalized[met_plot]) / ratio,
                        markersize=MARKERSIZE,
                        linewidth=LINEWIDTH,
                        zorder=2,
                        marker="*",
                        label="Real",
                        color="black",
                    )
                    xlims = ax.get_xlim()
                    ax.plot(
                        xlims,
                        [0, 0],
                        color="lightgrey",
                        zorder=1,
                    )
                    ax.set_xlim(xlims)
                else:
                    ax.plot(
                        df_real["xx"] / 10**3,
                        df_real[met_plot] / ratio,
                        markersize=MARKERSIZE,
                        linewidth=LINEWIDTH,
                        zorder=2,
                        marker="*",
                        label="Real",
                    )
                # Add growth
                for end_folder, pos in zip(END_FOLDERS, [0, 1, -2]):
                    df = pd.read_json(
                        FOLDEROOT
                        + end_folder
                        + f"/bs_{BUFF_SIZE}_{met}/metrics_growth.json"
                    )
                    if normalized:
                        val_df_normalize = [dict_real_normalized[met_plot][pos]]
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
                            markevery=MARKERDIST,
                            markersize=MARKERSIZE,
                            linewidth=LINEWIDTH,
                            zorder=2,
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
                            markevery=MARKERDIST,
                            markersize=MARKERSIZE,
                            linewidth=LINEWIDTH,
                            zorder=2,
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
                filename = folder_plot + f"/{met_plot}"
                if normalized:
                    filename += "_normalized"
                fig.savefig(filename + ".png")
                plt.close(fig=fig)


if __name__ == "__main__":
    main()

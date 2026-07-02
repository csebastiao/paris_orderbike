# -*- coding: utf-8 -*-
"""
Plot the AUC in additive order of all strategies on the tested graphs.
"""

import os
import json
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
from G_grow_bikenet import FOLDEROOT, END_FOLDERS
from J_plot_lineplot import FOLDERPLOT
from Ma_plot_AUC import is_pareto_efficient

# PLOT_LIMITS = [
#     [[0.35, 0.9], [0.35, 0.95]],
#     [[0.5, 0.8], [0.35, 0.95]],
#     [[0.6, 0.85], [0.35, 0.95]],
# ]

PLOT_LIMITS = [
    [[0.35, 0.95], [0.35, 0.95]],
    [[0.35, 0.95], [0.35, 0.95]],
    [[0.35, 0.95], [0.35, 0.95]],
]


def main():
    with open("./scripts/M_plot_AUC.json", "r") as f:
        plot_params = json.load(f)
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    fig, axs = plt.subplots(
        1,
        3,
        sharey="all",
        figsize=[plot_params["figsize"][0] * 3, plot_params["figsize"][1]],
        width_ratios=compute_width_ratios(PLOT_LIMITS),
    )
    savename_plot = FOLDERPLOT + "/AUC_plot_multiple.png"
    for idx, end_folder in enumerate(END_FOLDERS):
        ax = axs[idx]
        folder_data = FOLDEROOT + end_folder + "/"
        folder_plot = FOLDERPLOT + end_folder + "/AUC/"
        if not os.path.exists(folder_plot):
            os.makedirs(folder_plot)
        savename = folder_data + "/auc_table_growth"
        savename += ".json"
        df_growth = pd.read_json(savename)
        for ids, met in enumerate(plot_params["order"]):
            mask_met = df_growth["Metric optimized"] == met
            if met in ["random", "road_hierarchy"]:
                zorder = 2
            elif met == "real":
                zorder = 4
            else:
                zorder = 3
            ax.scatter(
                df_growth[mask_met]["AUC of Directness"],
                df_growth[mask_met]["AUC of Coverage"],
                linewidths=0,
                zorder=zorder,
                **{
                    key: val[ids]
                    for key, val in plot_params.items()
                    if key
                    not in [
                        "dpi",
                        "figsize",
                        "rcparams",
                        "order",
                        "errorbar_random",
                        "errorbar_hierarchy",
                    ]
                },
            )
            if met == "random":
                xx_mean = df_growth[mask_met]["AUC of Directness"].mean()
                xx_std = df_growth[mask_met]["AUC of Directness"].std()
                yy_mean = df_growth[mask_met]["AUC of Coverage"].mean()
                yy_std = df_growth[mask_met]["AUC of Coverage"].std()
                ax.errorbar(
                    x=xx_mean,
                    y=yy_mean,
                    yerr=yy_std,
                    xerr=xx_std,
                    fmt="o",
                    **{key: val for key, val in plot_params["errorbar_random"].items()},
                    zorder=3,
                )
            elif met == "road_hierarchy":
                xx_mean = df_growth[mask_met]["AUC of Directness"].mean()
                xx_std = df_growth[mask_met]["AUC of Directness"].std()
                yy_mean = df_growth[mask_met]["AUC of Coverage"].mean()
                yy_std = df_growth[mask_met]["AUC of Coverage"].std()
                ax.errorbar(
                    x=xx_mean,
                    y=yy_mean,
                    yerr=yy_std,
                    xerr=xx_std,
                    fmt="None",
                    capsize=0,
                    **{
                        key: val
                        for key, val in plot_params["errorbar_hierarchy"].items()
                    },
                    zorder=3,
                )
        ax.set_xlabel("AUC of directness")
        # Put ticks at each 0.1
        loc = mpl.ticker.MultipleLocator(base=0.1)
        ax.xaxis.set_major_locator(loc)
        ax.yaxis.set_major_locator(loc)
        ax.set(
            xlim=PLOT_LIMITS[idx][0],
            ylim=PLOT_LIMITS[idx][1],
            aspect="equal",
            adjustable="box",
        )
        ax.set_title(
            end_folder,
            fontdict={
                "fontweight": "bold",
                "fontsize": plot_params["rcparams"]["font.size"] * 2,
            },
        )
        parfront = df_growth.copy()
        parfront = parfront[
            parfront.apply(
                lambda x: is_pareto_efficient(
                    x, parfront, "AUC of Coverage", "AUC of Directness"
                ),
                axis=1,
            )
        ]
        parfront.sort_values("AUC of Directness", axis=0, inplace=True)
        ax.plot(
            parfront["AUC of Directness"],
            parfront["AUC of Coverage"],
            linestyle="dashed",
            linewidth=1,
            color="black",
            zorder=1,
            label="Pareto front",
        )
        if idx == 0:
            ax.set_ylabel("AUC of coverage")
            lgnd = ax.legend(
                prop={"size": plot_params["rcparams"]["font.size"] * 0.75},
                labelspacing=0.75,
                ncol=2,
            )
            for handle in lgnd.legend_handles[:-2]:
                handle._sizes = [70]
            lgnd.legend_handles[-3]._sizes = [120]
            lgnd.legend_handles[-2]._sizes = [120]
    fig.savefig(savename_plot)


def compute_width_ratios(lims):
    lengths = [arr[0][1] - arr[0][0] for arr in lims]
    total_length = sum(lengths)
    return [le / total_length for le in lengths]


if __name__ == "__main__":
    main()

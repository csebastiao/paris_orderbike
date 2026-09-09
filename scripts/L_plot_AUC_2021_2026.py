# -*- coding: utf-8 -*-
"""
Plot the AUC in additive order of all strategies on the tested graphs.
"""

import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
from G_grow_bikenet import FOLDEROOT
from K_plot_lineplot_covdir_merged_2021 import FOLDERPLOT

END_FOLDERS = [
    "2021",
    "2026",
]
PLOT_Y = [0.35, 0.95]
PLOT_X = [0.55, 0.85]
PARAMS_DICT = {
    "order": [
        "coverage",
        "directness",
        "betweenness",
        "dual_betweenness",
        "closeness",
        "dual_closeness",
        "road_hierarchy",
        "road_hierarchy_coverage",
        "road_hierarchy_directness",
        "random",
        "real_random",
    ],
    "label": [
        "Coverage",
        "Directness",
        "Betweenness",
        "Dual betweenness",
        "Closeness",
        "Dual closeness",
        "Hierarchical, random",
        "Hierarchical, coverage",
        "Hierarchical, directness",
        "Random",
        "Empirical",
    ],
    "color": [
        "#0173b2",
        "#d55e00",
        "#029e73",
        "#029e73",
        "#cc78bc",
        "#cc78bc",
        "#7E57C2",
        "#46afe8",
        "#ea914d",
        "#949494",
        "black",
    ],
    "marker": ["D", "s", "h", "P", "p", "X", "d", "d", "d", "o", "*"],
    "alpha": [0.65, 1, 1, 1, 1, 1, 0.3, 1, 1, 0.3, 1],
    "s": [70, 70, 70, 70, 70, 70, 40, 120, 120, 40, 200],
    "figsize": [11.69, 8.27],
    "errorbar_random": {"elinewidth": 1, "color": "#D0D0D0", "markersize": 6},
    "errorbar_hierarchy": {"elinewidth": 1, "color": "#D0D0D0"},
    "rcparams": {
        "font.size": 12,
        "font.family": "sans-serif",
        "font.sans-serif": "Arial",
        "axes.grid": "True",
        "axes.spines.right": "False",
        "axes.spines.top": "False",
        "axes.axisbelow": "True",
        "grid.color": "E1E1E1",
        "xtick.bottom": "True",
        "ytick.left": "True",
        "figure.frameon": "False",
        "figure.dpi": 500,
        "savefig.bbox": "tight",
        "legend.loc": "lower left",
        "legend.edgecolor": "black",
        "legend.facecolor": "F7F7F7",
        "errorbar.capsize": 4,
    },
}

# TODO add title
# TODO add horizontal legend


def main():
    for key in PARAMS_DICT["rcparams"]:
        mpl.rcParams[key] = PARAMS_DICT["rcparams"][key]
    fig, axs = plt.subplots(
        1,
        2,
        sharey="all",
        figsize=PARAMS_DICT["figsize"],
    )
    savename_plot = FOLDERPLOT + "AUC_2021_2026.png"
    for idx, end_folder in enumerate(END_FOLDERS):
        ax = axs[idx]
        ax.set_title(end_folder, y=0.975, fontweight=900)
        folder_data = FOLDEROOT + end_folder + "/"
        savename = folder_data + "/auc_table_growth"
        savename += ".json"
        df_growth = pd.read_json(savename)
        for ids, met in enumerate(PARAMS_DICT["order"]):
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
                    for key, val in PARAMS_DICT.items()
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
                    fmt="None",
                    capsize=2,
                    **{key: val for key, val in PARAMS_DICT["errorbar_random"].items()},
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
                    capsize=2,
                    **{
                        key: val
                        for key, val in PARAMS_DICT["errorbar_hierarchy"].items()
                    },
                    zorder=3,
                )
        ax.set_xlabel("AUC of directness")
        # Put ticks at each 0.1
        loc = mpl.ticker.MultipleLocator(base=0.1)
        ax.xaxis.set_major_locator(loc)
        ax.yaxis.set_major_locator(loc)
        ax.set(
            xlim=PLOT_X,
            ylim=PLOT_Y,
            aspect="equal",
            adjustable="box",
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
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    lgnd = fig.legend(
        by_label.values(),
        by_label.keys(),
        loc="outside upper center",
        prop={"size": PARAMS_DICT["rcparams"]["font.size"] * 0.9},
        labelspacing=0.5,
        ncol=4,
    )
    for handle in lgnd.legend_handles[:-2]:
        handle._sizes = [80]
    lgnd.legend_handles[-2]._sizes = [140]
    fig.subplots_adjust(wspace=-0.3)
    fig.savefig(savename_plot, bbox_inches="tight", pad_inches=0)


def is_pareto_efficient(x, df, fdim, sdim):
    return ~np.any(df[(df[fdim] > x[fdim]) & (df[sdim] > x[sdim])])


if __name__ == "__main__":
    main()

"""
Plot results for the Gini coefficient.
"""

import matplotlib as mpl
import numpy as np
import pandas as pd
from Ga_grow_bikenet import FOLDEROOT
from Kb_plot_lineplot_covdir_merged_supplementary import FOLDERPLOT_SUPP
from matplotlib import pyplot as plt

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
        "random_disconnected",
        "random_relaxed",
        "real_random",
    ],
    "label": [
        "Coverage",
        "Directness",
        "Betweenness",
        "Dual betweenness",
        "Closeness",
        "Dual closeness",
        "Hierarchy-random",
        "Hierarchy-coverage",
        "Hierarchy-directness",
        "Random",
        "Random-disconnected",
        "Random-relaxed",
        "Empirical",
    ],
    "color": [
        "#0173b2",
        "#d55e00",
        "#017856",
        "#017856",
        "#5BC93A",
        "#5BC93A",
        "#7E57C2",
        "#46afe8",
        "#ea914d",
        "#949494",
        "pink",
        "brown",
        "black",
    ],
    "marker": ["D", "s", "h", "P", "p", "X", "d", "d", "d", "o", "D", "P", "*"],
    "alpha": [0.65, 1, 1, 1, 1, 1, 0.3, 1, 1, 0.3, 0.3, 0.3, 1],
    "s": [70, 70, 70, 70, 70, 70, 40, 120, 120, 40, 40, 40, 200],
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
        "legend.edgecolor": "black",
        "legend.facecolor": "F7F7F7",
        "errorbar.capsize": 4,
    },
}
BUFFER_SIZE = 400
PLOT_LIMS_DICT = [[[0.5, 0.8], [0.75, 0.9], 0.05], [[0.5, 0.95], [0.75, 0.9], 0.05]]
EXP_GAP = 10


def main():
    for key in PARAMS_DICT["rcparams"]:
        mpl.rcParams[key] = PARAMS_DICT["rcparams"][key]
    for auc, auc_label, auc_lims in zip(
        ["AUC of Directness", "AUC of Coverage"],
        ["AUC of directness", "AUC of coverage"],
        PLOT_LIMS_DICT,
    ):
        fig, ax = plt.subplots(
            figsize=PARAMS_DICT["figsize"],
        )
        savename_plot = (
            FOLDERPLOT_SUPP
            + f"AUC_gini_2021_2026_bs_{BUFFER_SIZE}_{'_'.join(auc_label.split(' '))}.png"
        )
        folder_data = FOLDEROOT + "2021/"
        savename = folder_data + f"/auc_table_growth_bs_{BUFFER_SIZE}_alt"
        savename += ".json"
        df_growth = pd.read_json(savename)
        df_growth.loc[:, "AUC of Gini"] = 1 - df_growth["AUC of Gini"]
        df_growth = df_growth.drop([2027])
        for ids, met in enumerate(PARAMS_DICT["order"]):
            mask_met = df_growth["Metric optimized"] == met
            if met in [
                "random",
                "random_disconnected",
                "random_relaxed",
                "road_hierarchy",
            ]:
                zorder = 2
            elif met == "real":
                zorder = 4
            else:
                zorder = 3
            ax.scatter(
                df_growth[mask_met][auc],
                df_growth[mask_met]["AUC of Gini"],
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
            if met in ["random", "random_disconnected", "random_relaxed"]:
                xx_mean = df_growth[mask_met][auc].mean()
                xx_std = df_growth[mask_met][auc].std()
                yy_mean = df_growth[mask_met]["AUC of Gini"].mean()
                yy_std = df_growth[mask_met]["AUC of Gini"].std()
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
                xx_mean = df_growth[mask_met][auc].mean()
                xx_std = df_growth[mask_met][auc].std()
                yy_mean = df_growth[mask_met]["AUC of Gini"].mean()
                yy_std = df_growth[mask_met]["AUC of Gini"].std()
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
            elif met == "real_random":
                # Add Strong Pareto Improvment patch
                rect = mpl.patches.Rectangle(
                    (
                        df_growth[mask_met][auc],
                        df_growth[mask_met]["AUC of Gini"],
                    ),
                    auc_lims[0][-1] - df_growth[mask_met][auc].values[0],
                    auc_lims[1][-1] - df_growth[mask_met]["AUC of Gini"].values[0],
                    linewidth=0,
                    color="green",
                    alpha=0.1,
                    zorder=0,
                )
                ax.add_patch(rect)
        ax.set_xlabel(auc_label)
        ax.set_ylabel("1 - AUC of Gini")
        parfront = df_growth.copy()
        parfront = parfront[
            parfront.apply(
                lambda x: is_pareto_efficient(
                    x,
                    parfront,  # noqa: B023
                    "AUC of Gini",
                    auc,  # noqa: B023
                ),
                axis=1,
            )
        ]
        parfront.sort_values(auc, axis=0, inplace=True)
        ax.plot(
            parfront[auc],
            parfront["AUC of Gini"],
            linestyle="dashed",
            linewidth=1,
            color="black",
            zorder=1,
            label="Pareto front",
        )
        loc = mpl.ticker.MultipleLocator(base=auc_lims[-1])
        # ax.xaxis.set_major_locator(loc)
        ax.yaxis.set_major_locator(loc)
        ax.set(
            xlim=auc_lims[0],
            ylim=auc_lims[1],
            aspect="equal",
        )
        lgnd = ax.legend(
            prop={"size": PARAMS_DICT["rcparams"]["font.size"] * 0.76},
            labelspacing=0.5,
            ncol=4,
        )
        for handle in lgnd.legend_handles:
            handle._alpha = 1
        for handle in lgnd.legend_handles[:-2]:
            handle._sizes = [80]
        lgnd.legend_handles[-2]._sizes = [140]
        fig.savefig(savename_plot, bbox_inches="tight", pad_inches=0)


def is_pareto_efficient(x, df, fdim, sdim):
    return ~np.any(df[(df[fdim] > x[fdim]) & (df[sdim] > x[sdim])])


if __name__ == "__main__":
    main()

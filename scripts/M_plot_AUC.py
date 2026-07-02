# -*- coding: utf-8 -*-
"""
Plot the AUC in additive order of all strategies on the tested graphs.
"""

import os
import json
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
from G_grow_bikenet import FOLDEROOT, END_FOLDERS
from J_plot_lineplot import FOLDERPLOT

"#ea914d"


def main():
    with open("./scripts/M_plot_AUC.json", "r") as f:
        plot_params = json.load(f)
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    for end_folder in END_FOLDERS:
        folder_data = FOLDEROOT + end_folder + "/"
        folder_plot = FOLDERPLOT + end_folder + "/AUC/"
        if not os.path.exists(folder_plot):
            os.makedirs(folder_plot)
        savename = folder_data + "/auc_table_growth"
        savename += ".json"
        df_growth = pd.read_json(savename)
        fig, ax = plt.subplots(figsize=plot_params["figsize"])
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
        ax.set_ylabel("AUC of coverage")
        savename = folder_plot + f"/AUC_plot_{end_folder}"
        # Put ticks at each 0.1
        loc = mpl.ticker.MultipleLocator(base=0.1)
        ax.xaxis.set_major_locator(loc)
        ax.yaxis.set_major_locator(loc)
        plt.axis("square")
        # Set rounded limits at smallest and highest 0.1
        dirmin = df_growth["AUC of Directness"].min()
        dirmax = df_growth["AUC of Directness"].max()
        covmin = df_growth["AUC of Coverage"].min()
        covmax = df_growth["AUC of Coverage"].max()
        mmin = round(min(dirmin, covmin) - 0.05, 1)
        mmax = round(max(dirmax, covmax) + 0.05, 1)
        ax.set_xlim([mmin, mmax])
        ax.set_ylim([mmin, mmax])
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
        lgnd = ax.legend(
            prop={"size": plot_params["rcparams"]["font.size"] * 0.75},
            labelspacing=0.75,
            ncol=2,
        )
        for handle in lgnd.legend_handles[:-2]:
            handle._sizes = [70]
        lgnd.legend_handles[-3]._sizes = [120]
        lgnd.legend_handles[-2]._sizes = [120]
        fig.savefig(savename)
        plt.close(fig=fig)


def is_pareto_efficient(x, df, fdim, sdim):
    return ~np.any(df[(df[fdim] > x[fdim]) & (df[sdim] > x[sdim])])


def average_x(df):
    arr = []
    for ind in set(df.index):
        arr.append(df[df.index == ind].mean())
    return arr


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Plot the AUC in additive order of all strategies on the tested graphs.
"""

import os
import json
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
from G_grow_bikenet import FOLDEROOT
from J_plot_lineplot import FOLDERPLOT
from Ma_plot_AUC import is_pareto_efficient

END_FOLDERS = [
    "2021",
    "2026",
]
PLOT_Y = [0.35, 0.95]
XLIM_DICT = {
    "square": PLOT_Y,
    "thin": [0.55, 0.85],
}
COLOR_DICT = {
    "colorful": [0, 0],
    "sober": [
        "black",
        "black",
        "black",
        "#43B284FF",
        "black",
        "black",
        "#949494",
        "black",
        "#0F7BA2FF",
        "black",
        "#DD5129FF",
    ],
}


def main():
    with open("./scripts/M_plot_AUC.json", "r") as f:
        plot_params = json.load(f)
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    for colorname, colorlist in COLOR_DICT.items():
        for endname, xlim in XLIM_DICT.items():
            if endname == "square":
                fig, axs = plt.subplots(
                    1,
                    2,
                    sharey="all",
                    figsize=[plot_params["figsize"][0] * 2, plot_params["figsize"][1]],
                )
            elif endname == "thin":
                fig, axs = plt.subplots(
                    1,
                    2,
                    sharey="all",
                    figsize=[plot_params["figsize"][0], plot_params["figsize"][1]],
                )
            savename_plot = FOLDERPLOT + f"/AUC_plot_multiple_{endname}_{colorname}.png"
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
                    if colorname == "colorful":
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
                    elif colorname == "sober":
                        ax.scatter(
                            df_growth[mask_met]["AUC of Directness"],
                            df_growth[mask_met]["AUC of Coverage"],
                            linewidths=0,
                            zorder=zorder,
                            color=colorlist[ids],
                            alpha=1,
                            **{
                                key: val[ids]
                                for key, val in plot_params.items()
                                if key
                                not in [
                                    "dpi",
                                    "color",
                                    "alpha",
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
                            **{
                                key: val
                                for key, val in plot_params["errorbar_random"].items()
                            },
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
                                for key, val in plot_params[
                                    "errorbar_hierarchy"
                                ].items()
                            },
                            zorder=3,
                        )
                ax.set_xlabel("AUC of directness")
                # Put ticks at each 0.1
                loc = mpl.ticker.MultipleLocator(base=0.1)
                ax.xaxis.set_major_locator(loc)
                ax.yaxis.set_major_locator(loc)
                ax.set(
                    xlim=xlim,
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
                elif idx == 1:
                    if endname == "thin":
                        lgnd = ax.legend(
                            bbox_to_anchor=(1, 1),
                            prop={"size": plot_params["rcparams"]["font.size"] * 0.67},
                            labelspacing=0.67,
                            ncol=1,
                            loc="upper left",
                        )
                    elif endname == "square":
                        lgnd = ax.legend(
                            prop={"size": plot_params["rcparams"]["font.size"] * 0.67},
                            labelspacing=0.67,
                            ncol=1,
                            loc="upper left",
                        )
                    for handle in lgnd.legend_handles[:-2]:
                        handle._sizes = [80]
                    lgnd.legend_handles[-2]._sizes = [140]
            fig.subplots_adjust(wspace=0.2)
            fig.savefig(savename_plot, bbox_inches="tight", pad_inches=0)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Plot the metrics in additive order of all strategies on Paris bikenet, showing the average in AUC of Coverage and Directness for multiple trials.
"""

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
from J_compute_AUC import average_x

MARKERSIZE = 200
MARKERSIZE_IMPORTANT = 800
LINEWIDTH = 3
FOLDERPLOT = "./plots/article/"
MET_PLOT = {
    "coverage": "Coverage ($km^2$)",
    "directness": "Directness",
}
PARAMS_DICT = {
    "order": [
        "coverage",
        "directness",
        "dual_betweenness",
        "road_hierarchy_coverage",
        "road_hierarchy_directness",
        "real",
        "real_random",
    ],
    "label": [
        "Coverage",
        "Directness",
        "Dual betweenness",
        "Hierarchical, coverage",
        "Hierarchical, directness",
        "Empirical",
        "Empirical",
    ],
    "color": [
        "#0173b2",
        "#d55e00",
        "#029e73",
        "#46afe8",
        "#ea914d",
        "black",
        "dimgrey",
    ],
    "figsize": [11.69, 8.27 * 2],
    "rcparams": {
        "font.size": 20,
        "font.family": "sans-serif",
        "font.sans-serif": "Arial",
        "axes.grid": "False",
        "axes.spines.right": "False",
        "axes.spines.top": "False",
        "axes.axisbelow": "True",
        "grid.color": "E1E1E1",
        "xtick.bottom": "True",
        "ytick.left": "True",
        "figure.frameon": "False",
        "figure.dpi": 300,
        "savefig.bbox": "tight",
        "legend.edgecolor": "black",
        "legend.facecolor": "F7F7F7",
    },
}


def main():
    for key in PARAMS_DICT["rcparams"]:
        mpl.rcParams[key] = PARAMS_DICT["rcparams"][key]
    folder_data = FOLDEROOT + "2021/"
    avg = {}
    df_concat = pd.DataFrame()
    for i in range(NUM_RAND_TRIAL):
        df = pd.read_json(
            folder_data + f"bs_{BUFF_SIZE}_random/random_{i:03}/metrics_growth.json"
        )
        df_concat = pd.concat([df_concat, df])
    random_df = pd.DataFrame(average_x(df_concat))
    for met in PARAMS_DICT["order"]:
        foldermet = folder_data + f"bs_{BUFF_SIZE}_{met}/"
        if met in [
            "road_hierarchy",
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
    fig, axs = plt.subplots(2, 1, figsize=PARAMS_DICT["figsize"], sharex="col")
    for idx, (met_plot, met_label) in enumerate(MET_PLOT.items()):
        ax = axs[idx]
        if met_plot == "coverage":
            ratio = 10**6
        else:
            ratio = 1
        ax.set_ylabel(met_label)
        for ids, met in enumerate(PARAMS_DICT["order"]):
            ignore_keys = ["dpi", "figsize", "rcparams", "order"]
            if met == "real":
                ignore_keys.append("label")
            df = avg[met]
            if met == "real":
                zorder = 4
            elif met == "real_random":
                zorder = 2
            else:
                zorder = 3
            if met == "real":
                ax.scatter(
                    df["xx"] / 10**3,
                    df[met_plot] / ratio,
                    s=MARKERSIZE,
                    marker="*",
                    zorder=zorder,
                    **{
                        key: val[ids]
                        for key, val in PARAMS_DICT.items()
                        if key not in ignore_keys
                    },
                )
                df_important = df.iloc[[0, -2]]
                ax.scatter(
                    df_important["xx"] / 10**3,
                    df_important[met_plot] / ratio,
                    s=MARKERSIZE_IMPORTANT,
                    marker="*",
                    zorder=zorder,
                    **{
                        key: val[ids]
                        for key, val in PARAMS_DICT.items()
                        if key not in ignore_keys
                    },
                )
                if idx == 1:
                    for time, i, offset in zip(
                        ("2021", "2026"), (0, -2), ((0, -40), (30, -30))
                    ):
                        ax.annotate(
                            time,
                            xy=(
                                df.iloc[i]["xx"] / 10**3,
                                df.iloc[i][met_plot] / ratio,
                            ),
                            xytext=offset,
                            textcoords="offset points",
                            fontweight=900,
                            color="black",
                            ha="center",
                            va="center",
                        )
            elif met == "real_random":
                ax.plot(
                    df["xx"] / 10**3,
                    df[met_plot] / ratio,
                    linewidth=LINEWIDTH,
                    linestyle="dashed",
                    zorder=zorder,
                    **{
                        key: val[ids]
                        for key, val in PARAMS_DICT.items()
                        if key not in ignore_keys
                    },
                )
            else:
                ax.plot(
                    df["xx"] / 10**3,
                    df[met_plot] / ratio,
                    linewidth=LINEWIDTH,
                    zorder=zorder,
                    **{
                        key: val[ids]
                        for key, val in PARAMS_DICT.items()
                        if key not in ignore_keys
                    },
                )
        xlims = ax.get_xlim()
        ax.plot(
            random_df["xx"] / 10**3,
            random_df[met_plot] / ratio,
            linewidth=LINEWIDTH,
            color="grey",
            label="Random",
            zorder=2,
        )
        ax.set_xlim(xlims)
        ax.set_xlabel("Built length ($km$)")
        ax.set_axisbelow(True)
    fig.tight_layout()
    axs[0].legend()
    axs[0].set_xlabel("")
    fig.savefig(FOLDERPLOT + "/2021_lineplot_merged.png")
    plt.close(fig=fig)


if __name__ == "__main__":
    main()

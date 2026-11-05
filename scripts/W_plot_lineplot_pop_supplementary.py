"""Plot the lineplot of number of components for the real order and all random strategies."""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from Ga_grow_bikenet import FOLDEROOT
from Kb_plot_lineplot_covdir_merged_supplementary import FOLDERPLOT_SUPP

BUFFER_SIZE = 400
NUM_TRIAL = 1000
PARAMS_DICT = {
    "order": [
        "coverage",
        "directness",
        "dual_betweenness",
        "road_hierarchy_coverage",
        "road_hierarchy_directness",
        "real_random",
        "random",
        "random_disconnected",
        "random_relaxed",
    ],
    "label": [
        "Coverage",
        "Directness",
        "Dual betweenness",
        "Hierarchy-coverage",
        "Hierarchy-directness",
        "Empirical",
        "Random",
        "Random-disconnected",
        "Random-relaxed",
    ],
    "color": [
        "#0173b2",
        "#d55e00",
        "#017856",
        "#46afe8",
        "#ea914d",
        "#B0B0B0",
        "#949494",
        "pink",
        "brown",
    ],
    "figsize": [11.69, 8.27],
    "rcparams": {
        "font.size": 10,
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


# TODO harmonize values with other plots
def main():
    for key in PARAMS_DICT["rcparams"]:
        mpl.rcParams[key] = PARAMS_DICT["rcparams"][key]
    fig, ax = plt.subplots(figsize=PARAMS_DICT["figsize"])
    df = pd.read_json(FOLDEROOT + f"2021/bs_{BUFFER_SIZE}_real/metrics_growth.json")
    ax.scatter(
        df["xx"].values / 10**3,
        df["pop"].values / 10**6,
        color="black",
        marker="*",
        s=200,
        zorder=3,
    )
    for met, metname, color in zip(
        PARAMS_DICT["order"], PARAMS_DICT["label"], PARAMS_DICT["color"]
    ):
        if met in [
            "real_random",
            "random",
            "random_disconnected",
            "random_relaxed",
        ]:
            pop = []
            xx = []
            for i in range(NUM_TRIAL):
                df = pd.read_json(
                    FOLDEROOT
                    + f"2021/bs_{BUFFER_SIZE}_{met}/{met}_{i:03}/metrics_growth.json"
                )
                pop.append(df["pop"].values)
                xx.append(df["xx"].values)
            pop = np.mean(np.transpose(pop), axis=1)
            xx = np.mean(np.transpose(xx), axis=1)
            ax.plot(xx / 10**3, pop / 10**6, color=color, label=metname, linewidth=3)
        elif met == "coverage":
            pop = []
            xx = []
            for i in range(20):
                df = pd.read_json(
                    FOLDEROOT
                    + f"2021/bs_{BUFFER_SIZE}_{met}/{met}_{i:03}/metrics_growth.json"
                )
                pop.append(df["pop"].values)
                xx.append(df["xx"].values)
            pop = np.mean(np.transpose(pop), axis=1)
            xx = np.mean(np.transpose(xx), axis=1)
            ax.plot(xx / 10**3, pop / 10**6, color=color, label=metname, linewidth=3)
        else:
            df = pd.read_json(
                FOLDEROOT + f"2021/bs_{BUFFER_SIZE}_{met}/metrics_growth.json"
            )
            ax.plot(
                df["xx"] / 10**3,
                df["pop"] / 10**6,
                color=color,
                label=metname,
                linewidth=3,
            )
    ax.set_xlabel("Built length (km)")
    ax.set_ylabel("Population covered (millions)")
    ax.legend()
    fig.savefig(
        FOLDERPLOT_SUPP + f"/2021_lineplot_pop_bs_{BUFFER_SIZE}.png", pad_inches=0.0
    )
    plt.close(fig=fig)


if __name__ == "__main__":
    main()

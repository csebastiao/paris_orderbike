# -*- coding: utf-8 -*-
"""
Plot the metrics in additive order of all hierarchical orders on Paris bikenet, showing the average in AUC of Coverage and Directness for multiple trials.
"""

import os
import json
import geopandas as gpd
import momepy as mp
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
from G_grow_bikenet import (
    BUFF_SIZE,
    FOLDEROOT,
)
from I_plot_lineplot import FOLDERPLOT

ROAD_HIERARCHY = [
    "primary",
    "secondary",
    "tertiary",
    "quaternary",
]
COLOR_HIERARCHY = [
    "red",
    "orange",
    "blue",
    "purple",
]


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
    with open("./scripts/J_plot_lineplot_hierarchy.json", "r") as f:
        plot_params = json.load(f)
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    folder_data = FOLDEROOT + "Nothing/"
    folder_plot = FOLDERPLOT + "Nothing/lineplot_hierarchical/"
    if not os.path.exists(folder_plot):
        os.makedirs(folder_plot)
    avg = {}
    for met in plot_params["order"]:
        foldermet = folder_data + f"bs_{BUFF_SIZE}_{met}/"
        if met == "road_hierarchy":
            df_concat = pd.DataFrame()
            num_step = 20  # TODO change to NUM_HIER_TRIAL later
            for i in range(num_step):
                df = pd.read_json(foldermet + f"{met}_{i:03}/metrics_growth.json")
                df_concat = pd.concat([df_concat, df])
            df_avg = pd.DataFrame(average_x(df_concat))
        else:
            df_avg = pd.read_json(foldermet + "metrics_growth.json")
        avg[met] = df_avg
    for met_plot, met_label in {
        "coverage": "Coverage ($km^2$)",
        "directness": "Directness",
    }.items():
        fig, ax = plt.subplots(figsize=plot_params["figsize"])
        if met_plot == "coverage":
            ratio = 10**6
        else:
            ratio = 1
        ax.set_ylabel(met_label)
        for ids, met in enumerate(plot_params["order"]):
            df = avg[met]
            if met == "real":
                ax.plot(
                    df["xx"] / 10**3,
                    df[met_plot] / ratio,
                    marker="*",
                    markersize=10,
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
                    **{
                        key: val[ids]
                        for key, val in plot_params.items()
                        if key not in ["dpi", "figsize", "rcparams", "order"]
                    },
                )
        ylim = ax.get_ylim()[1]
        # Add lines
        for i in range(len(ROAD_HIERARCHY)):
            H = G.edge_subgraph(
                [
                    edge
                    for edge in G.edges
                    if G.edges[edge]["highway"] in ROAD_HIERARCHY[: i + 1]
                ]
            )
            xx = sum([H.edges[e]["length"] for e in H.edges]) / 10**3
            ax.plot(
                [xx, xx],
                [0, ax.get_ylim()[1]],
                color=COLOR_HIERARCHY[i],
                linestyle="dashed",
                label=ROAD_HIERARCHY[i],
            )
        ax.set_ylim([0, ylim])
        ax.set_xlabel("Built length ($km$)")
        ax.set_axisbelow(True)
        fig.tight_layout()
        ax.legend()
        fig.savefig(folder_plot + f"/{met_plot}.png")
        plt.close(fig=fig)


def average_x(df):
    arr = []
    for ind in set(df.index):
        arr.append(df[df.index == ind].mean())
    return arr


if __name__ == "__main__":
    main()

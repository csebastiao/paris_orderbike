# -*- coding: utf-8 -*-
"""
Plot map of the bicycle network, showing either the road hierarchy next to the bicycle lanes or the time that the bicycle lane was built.
"""

import geopandas as gpd
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib_map_utils.core.scale_bar import scale_bar
import momepy as mp
import numpy as np
import json
from G_grow_bikenet import FOLDEROOT, BUFF_SIZE
from H_grow_linear_real_bikenet import TIMESTAMPS
from K_plot_lineplot_covdir_merged_2021 import FOLDERPLOT

FIGSIZE = [11.69 * 3, 8.27]
TITLES = ["Real", "Hierarchy, coverage", "Dual Betweenness"]
RCPARAMS = {
    "font.size": 25,
    "font.family": "sans-serif",
    "font.sans-serif": "Arial",
    "legend.loc": "upper left",
    "legend.frameon": False,
    "figure.dpi": 200,
}
COLOR_OLD = "black"
COLOR_NEW = "black"


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    size_int = gdf_edges[gdf_edges["built_in"].isin(TIMESTAMPS[:-1])]["length"].sum()
    G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
    for key in RCPARAMS:
        mpl.rcParams[key] = RCPARAMS[key]
    fig, axs = plt.subplots(1, 3, figsize=FIGSIZE)
    for idx, met in enumerate(["real", "road_hierarchy_coverage", "dual_betweenness"]):
        ax = axs[idx]
        ax.set_title(TITLES[idx])
        foldermet = FOLDEROOT + f"2021/bs_{BUFF_SIZE}_{met}/"
        if idx == 0:
            scale_bar(
                ax,
                location="lower left",
                style="ticks",
                bar={
                    "projection": gdf_edges.crs,
                    "unit": "km",
                    "major_mult": 1,
                    "major_div": 3,
                    "height": 0.1,
                },
                labels={
                    "style": "first_last",
                    "fontsize": RCPARAMS["font.size"],
                    "sep": 0.05,
                },
            )
            gdf_edges[gdf_edges["built_in"].isin(TIMESTAMPS[:-1])].plot(
                ax=ax,
                color="black",
                linewidth=3,
                zorder=4,
                capstyle="round",
                joinstyle="round",
            )
            ax.axis("off")
        else:
            with open(foldermet + "order_growth.json") as f:
                order_growth = json.load(f)
            order_growth = [
                tuple((tuple(val[0]), tuple(val[1]), val[2])) for val in order_growth
            ]
            with open(foldermet + "metrics_growth.json") as f:
                metrics_growth = json.load(f)
            gdf_edges[gdf_edges["built_in"] == TIMESTAMPS[0]].plot(
                ax=ax,
                color="black",
                linewidth=3,
                zorder=4,
                capstyle="round",
                joinstyle="round",
            )
            idx_stage = find_closest_value_idx(metrics_growth["xx"], size_int)
            H = G.edge_subgraph(order_growth[: idx_stage + 2])
            temp_gdf_edges = mp.nx_to_gdf(H, points=False, lines=True)
            temp_gdf_edges.plot(
                ax=ax,
                color="black",
                zorder=5,
                linewidth=3,
                capstyle="round",
                joinstyle="round",
            )
            ax.axis("off")
    fig.subplots_adjust(wspace=-0.2)
    fig.savefig(
        FOLDERPLOT + "Bikenet_2021_real_hc_db.png",
        bbox_inches="tight",
        pad_inches=0,
    )
    plt.close(fig=fig)


def find_closest_value_idx(list_values, target_value):
    lst = np.asarray(list_values)
    return (np.abs(lst - target_value)).argmin()


if __name__ == "__main__":
    main()

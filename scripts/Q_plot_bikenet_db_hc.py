# -*- coding: utf-8 -*-
"""
Plot map of the bicycle network, showing either the road hierarchy next to the bicycle lanes or the time that the bicycle lane was built.
"""

import os
import geopandas as gpd
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib_map_utils.core.scale_bar import scale_bar
import momepy as mp
import numpy as np
import json
from G_grow_bikenet import FOLDEROOT, BUFF_SIZE
from H_grow_linear_real_bikenet import TIMESTAMPS
from O_plot_bikenet_single_map import FOLDERMAPS, FIGSIZE, DPI, RCPARAMS


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    size_int = gdf_edges[gdf_edges["built_in"].isin(TIMESTAMPS[:-1])]["length"].sum()
    G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
    if not os.path.exists(FOLDERMAPS):
        os.makedirs(FOLDERMAPS)
    for key in RCPARAMS:
        mpl.rcParams[key] = RCPARAMS[key]
    fig, axs = plt.subplots(1, 2, figsize=FIGSIZE)
    for idx, met in enumerate(["road_hierarchy_coverage", "dual_betweenness"]):
        ax = axs[idx]
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
        foldermet = FOLDEROOT + f"2021/bs_{BUFF_SIZE}_{met}/"
        with open(foldermet + "order_growth.json") as f:
            order_growth = json.load(f)
        order_growth = [
            tuple((tuple(val[0]), tuple(val[1]), val[2])) for val in order_growth
        ]
        with open(foldermet + "metrics_growth.json") as f:
            metrics_growth = json.load(f)
        idx_stage = find_closest_value_idx(metrics_growth["xx"], size_int)
        gdf_edges[gdf_edges["built_in"] == TIMESTAMPS[0]].plot(
            ax=ax,
            color="black",
            linewidth=2,
            zorder=4,
        )
        H = G.edge_subgraph(order_growth[: idx_stage + 2])
        temp_gdf_edges = mp.nx_to_gdf(H, points=False, lines=True)
        temp_gdf_edges.plot(ax=ax, color="green", zorder=5, linewidth=3)
        gdf_edges.plot(
            ax=ax,
            color="#D0D0D0",
            linewidth=1,
            zorder=3,
        )
        ax.axis("off")
    fig.subplots_adjust(wspace=-0.2)
    fig.savefig(
        FOLDERMAPS + "Bikenet_growth_hc_db.png",
        dpi=DPI,
        bbox_inches="tight",
        pad_inches=0,
    )
    plt.close(fig=fig)


def find_closest_value_idx(list_values, target_value):
    lst = np.asarray(list_values)
    return (np.abs(lst - target_value)).argmin()


if __name__ == "__main__":
    main()

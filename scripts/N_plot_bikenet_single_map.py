# -*- coding: utf-8 -*-
"""
Plot map of the bicycle network, showing either the road hierarchy next to the bicycle lanes or the time that the bicycle lane was built.
"""

import os
import geopandas as gpd
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from C_process_joined_pes import TIMESTAMPS
from G_grow_bikenet import FOLDEROOT
from I_plot_lineplot import FOLDERPLOT
from J_plot_lineplot_hierarchy import ROAD_HIERARCHY, COLOR_HIERARCHY

FOLDERMAPS = FOLDERPLOT + "maps/"
FIGSIZE = [11.69, 8.27]
LINEWIDTH = 2
DPI = 300
RCPARAMS = {
    "font.size": 10,
    "font.family": "sans-serif",
    "font.sans-serif": "Arial",
    "legend.edgecolor": "black",
    "legend.facecolor": "F7F7F7",
    "legend.loc": "upper left",
}
COLOR_BEG = "grey"
COLOR_TIMESTAMPS = [
    plt.get_cmap("summer")(val) for val in np.linspace(0, 1, len(TIMESTAMPS))
]
COLOR_END = "red"


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    if not os.path.exists(FOLDERMAPS):
        os.makedirs(FOLDERMAPS)
    for key in RCPARAMS:
        mpl.rcParams[key] = RCPARAMS[key]
    # Plot the hierarchy
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for i in range(len(ROAD_HIERARCHY)):
        gdf_edges[gdf_edges["highway"] == ROAD_HIERARCHY[i]].plot(
            ax=ax,
            color=COLOR_HIERARCHY[i],
            linewidth=LINEWIDTH,
            label=ROAD_HIERARCHY[i],
            zorder=5 - i,
        )
    ax.legend()
    ax.axis("off")
    fig.savefig(
        FOLDERMAPS + "Road_hierarchy.png", dpi=DPI, bbox_inches="tight", pad_inches=0
    )
    plt.close(fig=fig)
    # Plot the time built
    fig, ax = plt.subplots(figsize=FIGSIZE)
    gdf_edges[gdf_edges["built_in"] == "2021-01-01"].plot(
        ax=ax,
        color=COLOR_BEG,
        linewidth=LINEWIDTH,
        label="Built before 2021",
        zorder=10,
    )
    for i in range(len(TIMESTAMPS)):
        gdf_edges[gdf_edges["built_in"] == TIMESTAMPS[i]].plot(
            ax=ax,
            color=COLOR_TIMESTAMPS[i],
            linewidth=LINEWIDTH,
            label=f"Built at {TIMESTAMPS[i]}",
            zorder=10 - 1 - i,
        )
    gdf_edges[gdf_edges["built_in"] == "No"].plot(
        ax=ax,
        color=COLOR_END,
        linewidth=LINEWIDTH,
        label="Not built yet",
        zorder=10 - 2 - len(TIMESTAMPS),
    )
    ax.legend()
    ax.axis("off")
    fig.savefig(
        FOLDERMAPS + "Time_built.png", dpi=DPI, bbox_inches="tight", pad_inches=0
    )
    plt.close(fig=fig)


if __name__ == "__main__":
    main()

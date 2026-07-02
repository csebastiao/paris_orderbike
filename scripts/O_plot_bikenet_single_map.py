# -*- coding: utf-8 -*-
"""
Plot map of the bicycle network, showing either the road hierarchy next to the bicycle lanes or the time that the bicycle lane was built.
"""

import os
import geopandas as gpd
import matplotlib as mpl
from matplotlib import pyplot as plt
from G_grow_bikenet import FOLDEROOT
from J_plot_lineplot import FOLDERPLOT

FOLDERMAPS = FOLDERPLOT + "maps/"
FIGSIZE = [11.69, 8.27]
ROAD_HIERARCHY = [
    "primary",
    "secondary",
    "tertiary",
    "quaternary",
]
COLOR_HIERARCHY = [
    "#000000",
    "#505050",
    "#A0A0A0",
    "#E0E0E0",
]
LINEWIDTHS_HIERARCHY = [
    3.5,
    2.75,
    2,
    1,
]
DPI = 300
RCPARAMS = {
    "font.size": 10,
    "font.family": "sans-serif",
    "font.sans-serif": "Arial",
    "legend.edgecolor": "black",
    "legend.facecolor": "F7F7F7",
    "legend.loc": "upper left",
}


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    if not os.path.exists(FOLDERMAPS):
        os.makedirs(FOLDERMAPS)
    for key in RCPARAMS:
        mpl.rcParams[key] = RCPARAMS[key]
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for i in range(len(ROAD_HIERARCHY)):
        gdf_edges[gdf_edges["highway"] == ROAD_HIERARCHY[i]].plot(
            ax=ax,
            color=COLOR_HIERARCHY[i],
            linewidth=LINEWIDTHS_HIERARCHY[i],
            label=ROAD_HIERARCHY[i],
            zorder=5 - i,
        )
    ax.legend()
    ax.axis("off")
    fig.savefig(
        FOLDERMAPS + "Road_hierarchy.png", dpi=DPI, bbox_inches="tight", pad_inches=0
    )
    plt.close(fig=fig)


if __name__ == "__main__":
    main()

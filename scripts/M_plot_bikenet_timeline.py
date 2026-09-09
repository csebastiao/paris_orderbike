# -*- coding: utf-8 -*-
"""
Plot map of the bicycle network timeline.
"""

import geopandas as gpd
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib_map_utils.core.scale_bar import scale_bar
from G_grow_bikenet import FOLDEROOT
from H_grow_linear_real_bikenet import TIMESTAMPS
from K_plot_lineplot_covdir_merged_2021 import FOLDERPLOT

FIGSIZE = [11.69, 8.27]
LINEWIDTHS_HIERARCHY = [
    3.5,
    2.75,
    2,
    1.2,
]
RCPARAMS = {
    "font.size": 15,
    "font.family": "sans-serif",
    "font.sans-serif": "Arial",
    "legend.loc": "upper left",
    "legend.frameon": False,
    "figure.dpi": 300,
}
COLOR_NEW = "#129D00"
COLOR_OLD = "black"
COLOR_MISSING = "#FF0000"


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    for key in RCPARAMS:
        mpl.rcParams[key] = RCPARAMS[key]
    fig, ax = plt.subplots(figsize=FIGSIZE)
    gdf_edges[gdf_edges["built_in"] == TIMESTAMPS[0]].plot(
        ax=ax,
        color=COLOR_OLD,
        linewidth=3,
        label="Built by 2021",
        zorder=4,
        capstyle="round",
        joinstyle="round",
    )
    gdf_edges[gdf_edges["built_in"].isin(TIMESTAMPS[1:-1])].plot(
        ax=ax,
        color=COLOR_NEW,
        linewidth=5,
        label="Built from 2021 to 2026",
        zorder=5,
        capstyle="round",
        joinstyle="round",
    )
    gdf_edges.plot(
        ax=ax,
        color=COLOR_MISSING,
        linewidth=1.2,
        label="Not yet built",
        zorder=3,
        capstyle="round",
        joinstyle="round",
    )
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
    ax.legend()
    ax.axis("off")
    fig.savefig(
        FOLDERPLOT + "Bikenet_timeline.png",
        bbox_inches="tight",
        pad_inches=0,
    )
    plt.close(fig=fig)


if __name__ == "__main__":
    main()

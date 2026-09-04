# -*- coding: utf-8 -*-
"""
Plot map of the bicycle network, showing either the road hierarchy next to the bicycle lanes or the time that the bicycle lane was built.
"""

import os
import geopandas as gpd
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib_map_utils.core.scale_bar import scale_bar
from G_grow_bikenet import FOLDEROOT
from H_grow_linear_real_bikenet import TIMESTAMPS
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
    1.2,
]
DPI = 300
RCPARAMS = {
    "font.size": 15,
    "font.family": "sans-serif",
    "font.sans-serif": "Arial",
    "legend.loc": "upper left",
    "legend.frameon": False,
}
COLOR_SCHEME_DICT = {"colorful": ["#808080", "#FF0000"], "sober": ["black", "#A0A0A0"]}


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    if not os.path.exists(FOLDERMAPS):
        os.makedirs(FOLDERMAPS)
    for key in RCPARAMS:
        mpl.rcParams[key] = RCPARAMS[key]
    fig, ax = plt.subplots(1, figsize=FIGSIZE)
    # Plot hierarchy
    for i in range(len(ROAD_HIERARCHY)):
        gdf_edges[gdf_edges["highway"] == ROAD_HIERARCHY[i]].plot(
            ax=ax,
            color=COLOR_HIERARCHY[i],
            linewidth=LINEWIDTHS_HIERARCHY[i],
            label=ROAD_HIERARCHY[i],
            zorder=5 - i,
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
        labels={"style": "first_last", "fontsize": RCPARAMS["font.size"], "sep": 0.05},
    )
    ax.axis("off")
    ax.legend()
    fig.savefig(
        FOLDERMAPS + "Bikenet_hierarchy.png", dpi=DPI, bbox_inches="tight", pad_inches=0
    )
    plt.close(fig=fig)
    for color_scheme in ["colorful", "sober"]:
        fig, ax = plt.subplots(1, figsize=FIGSIZE)
        # Plot chronology
        gdf_edges[gdf_edges["built_in"] == TIMESTAMPS[0]].plot(
            ax=ax,
            color=COLOR_SCHEME_DICT[color_scheme][0],
            linewidth=3,
            label="Built by 2021",
            zorder=4,
            capstyle="round",
            joinstyle="round",
        )
        gdf_edges[gdf_edges["built_in"].isin(TIMESTAMPS[1:-1])].plot(
            ax=ax,
            color="#129D00",
            linewidth=5,
            label="Built from 2021 to 2026",
            zorder=5,
            capstyle="round",
            joinstyle="round",
        )
        gdf_edges.plot(
            ax=ax,
            color=COLOR_SCHEME_DICT[color_scheme][1],
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
            FOLDERMAPS + f"Bikenet_timeline_{color_scheme}.png",
            dpi=DPI,
            bbox_inches="tight",
            pad_inches=0,
        )
        plt.close(fig=fig)


if __name__ == "__main__":
    main()

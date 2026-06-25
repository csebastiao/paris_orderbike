# -*- coding: utf-8 -*-
"""
Plot paris bicycle network growth at four timestamps.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
from G_grow_bikenet import FOLDEROOT
from H_compute_real_growth_bikenet import TIMESTAMPS
from N_plot_bikenet_single_map import FOLDERMAPS


GPKG_PATH = "./data/raw/paris_en_selle_map_updates/cleaned.gpkg"
SAVEPATH = "./data/processed/paris_simplified_results/"
DPI = 250
FIGSIZE = [11.69, 8.27]
COLOR_OLD = "black"
COLOR_NEW = "green"


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    fig, axs = plt.subplots(2, 2, figsize=FIGSIZE, layout="constrained")
    axs[0][0].axis("off")
    axs[0][0].set_title(TIMESTAMPS[0], fontname="Arial", fontsize=20, fontweight="bold")
    axs[0][1].set_title(TIMESTAMPS[1], fontname="Arial", fontsize=20, fontweight="bold")
    axs[1][0].set_title(
        TIMESTAMPS[-2], fontname="Arial", fontsize=20, fontweight="bold"
    )
    axs[1][1].set_title(
        TIMESTAMPS[-1], fontname="Arial", fontsize=20, fontweight="bold"
    )
    axs[0][1].axis("off")
    axs[1][0].axis("off")
    axs[1][1].axis("off")
    # Do in 2021
    gdf_edges[gdf_edges["built_in"] == TIMESTAMPS[0]].plot(
        ax=axs[0][0], color=COLOR_OLD
    )
    # Do in 2023
    gdf_edges[gdf_edges["built_in"] == TIMESTAMPS[0]].plot(
        ax=axs[0][1], color=COLOR_OLD
    )
    gdf_edges[gdf_edges["built_in"] == TIMESTAMPS[1]].plot(
        ax=axs[0][1], color=COLOR_NEW
    )
    # Do in 2026
    gdf_edges[gdf_edges["built_in"].isin(TIMESTAMPS[:2])].plot(
        ax=axs[1][0], color=COLOR_OLD
    )
    gdf_edges[gdf_edges["built_in"].isin(TIMESTAMPS[2:-2])].plot(
        ax=axs[1][0], color=COLOR_NEW
    )
    # Do in total
    gdf_edges[gdf_edges["built_in"].isin(TIMESTAMPS[:-1])].plot(
        ax=axs[1][1], color=COLOR_OLD
    )
    gdf_edges[gdf_edges["built_in"] == TIMESTAMPS[-1]].plot(
        ax=axs[1][1], color=COLOR_NEW
    )
    fig.savefig(FOLDERMAPS + "Bikenet_growth.png", dpi=DPI)


if __name__ == "__main__":
    main()

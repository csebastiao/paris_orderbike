# -*- coding: utf-8 -*-
"""
Plot maps of the bicycle network at different timestamps.
"""

import json
import geopandas as gpd
import momepy as mp
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from G_grow_bikenet import FOLDEROOT, BUFF_SIZE
from N_plot_bikenet_single_map import FOLDERMAPS


GROWTH_STRATEGIES = {
    "coverage": "Coverage",
    "road_hierarchy_coverage": "Hierarchy,\ncoverage",
    "dual_betweenness": "Dual\nbetweenness",
    "road_hierarchy_directness": "Hierarchy,\ndirectness",
    "directness": "Directness",
}
FIGSIZE = [11.69 * 3, 8.27 * len(GROWTH_STRATEGIES)]
RCPARAMS = {
    "font.size": 60,
    "font.family": "sans-serif",
    "font.sans-serif": "Arial",
}
LABEL_PAD = 80
DPI = 300
CHOICE = 0
LW = 3
COLOR_NEW = "green"


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    bb = gdf_edges.total_bounds
    G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
    closeness = nx.closeness_centrality(G, distance="length")
    edge_closeness = {
        edge: (closeness[edge[0]] + closeness[edge[1]]) / 2
        for edge in G.edges
        if (
            (G.edges[edge]["highway"] == "primary")
            & (G.edges[edge]["level"] == "primary")
        )
    }
    init_edge = [tuple(max(edge_closeness, key=edge_closeness.get))]
    len_beg = round(
        gdf_edges[gdf_edges["built_in"] == "2021-01-01"]["length"].sum() / 10**3
    )
    len_end = round(gdf_edges[gdf_edges["built_in"] != "No"]["length"].sum() / 10**3)
    stages = [len_beg - (len_end - len_beg), len_beg, len_end]
    for key in RCPARAMS:
        mpl.rcParams[key] = RCPARAMS[key]
    fig, axs = plt.subplots(len(GROWTH_STRATEGIES) + 1, len(stages), figsize=FIGSIZE)
    for idx_met, (met, met_name) in enumerate(GROWTH_STRATEGIES.items()):
        idx_stage_bef = 0
        axs[idx_met][0].set_ylabel(met_name, labelpad=LABEL_PAD)
        foldermet = FOLDEROOT + f"Nothing/bs_{BUFF_SIZE}_{met}/"
        if met == "coverage":
            foldermet += f"{met}_{CHOICE:03}/"
        with open(foldermet + "order_growth.json") as f:
            order_growth = json.load(f)
        order_growth = [
            tuple((tuple(val[0]), tuple(val[1]), val[2])) for val in order_growth
        ]
        with open(foldermet + "metrics_growth.json") as f:
            metrics_growth = json.load(f)
        for idx_sta, stage in enumerate(stages):
            ax = axs[idx_met][idx_sta]
            # Find the stage closest to the number of kilometer chosen
            idx_stage = find_closest_value_idx(metrics_growth["xx"], stage * 10**3)
            if idx_sta == 0:
                H = G.edge_subgraph(init_edge)
                temp_gdf_edges = mp.nx_to_gdf(H, points=False, lines=True)
                temp_gdf_edges.plot(ax=ax, color="black", zorder=2, linewidth=LW)
                H = G.edge_subgraph(order_growth[: idx_stage + 2])
                temp_gdf_edges = mp.nx_to_gdf(H, points=False, lines=True)
                temp_gdf_edges.plot(ax=ax, color=COLOR_NEW, zorder=3, linewidth=LW + 2)
            else:
                H = G.edge_subgraph(order_growth[: idx_stage_bef + 2])
                temp_gdf_edges = mp.nx_to_gdf(H, points=False, lines=True)
                temp_gdf_edges.plot(ax=ax, color="black", zorder=2, linewidth=LW)
                H = G.edge_subgraph(order_growth[idx_stage_bef + 1 : idx_stage + 2])
                temp_gdf_edges = mp.nx_to_gdf(H, points=False, lines=True)
                temp_gdf_edges.plot(ax=ax, color=COLOR_NEW, zorder=3, linewidth=LW + 2)
            idx_stage_bef = idx_stage
            ax.set_xlim([bb[0], bb[2]])
            ax.set_ylim([bb[1], bb[3]])
            ax.spines[:].set_visible(False)
            ax.set_xticks([])
            ax.set_yticks([])
            if idx_sta == 2:
                gdf_edges.plot(ax=ax, color="#E0E0E0", zorder=1, linewidth=LW - 1.5)
    axs[-1][0].set_ylabel("Real", labelpad=LABEL_PAD, multialignment="center")
    gdf_edges[gdf_edges["built_in"] == "2021-01-01"].plot(ax=axs[-1][0], color="white")
    gdf_edges[gdf_edges["built_in"] == "2021-01-01"].plot(
        ax=axs[-1][1], color=COLOR_NEW, linewidth=LW + 2
    )
    gdf_edges[gdf_edges["built_in"] == "2021-01-01"].plot(
        ax=axs[-1][2], color="black", linewidth=LW
    )
    gdf_edges[~gdf_edges["built_in"].isin(["No", "2021-01-01"])].plot(
        ax=axs[-1][2], color=COLOR_NEW, linewidth=LW + 2
    )
    gdf_edges[gdf_edges["built_in"] == "No"].plot(
        ax=axs[-1][2], color="#E0E0E0", linewidth=LW - 1.5
    )
    for i in range(len(stages)):
        ax = axs[-1][i]
        ax.set_xlim([bb[0], bb[2]])
        ax.set_ylim([bb[1], bb[3]])
        ax.spines[:].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
    for idx_sta, stage in enumerate(stages):
        axs[0][idx_sta].xaxis.set_label_position("top")
        axs[0][idx_sta].set_xlabel(f"${stage} km$", labelpad=LABEL_PAD)
    fig.tight_layout()
    fig.savefig(
        FOLDERMAPS + "Growth_steps_pareto.png",
        dpi=DPI,
        bbox_inches="tight",
        pad_inches=0.01,
    )


def find_closest_value_idx(list_values, target_value):
    lst = np.asarray(list_values)
    return (np.abs(lst - target_value)).argmin()


if __name__ == "__main__":
    main()

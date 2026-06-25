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
    "road_hierarchy_coverage": "Hierarchy (coverage)",
    "dual_betweenness": "Dual betweenness",
    "road_hierarchy_directness": "Hierarchy (directness)",
    "directness": "Directness",
}
STAGES = [
    50,
    100,
    150,
    200,
]
FIGSIZE = [11.69 * len(STAGES), 8.27 * len(GROWTH_STRATEGIES)]
RCPARAMS = {
    "font.size": 60,
    "font.family": "sans-serif",
    "font.sans-serif": "Arial",
    "figure.subplot.hspace": 0.005,
}
LABEL_PAD = 80
BB_PAD = 0.0002
DPI = 300
CHOICE = 0


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    bb = gdf_edges.total_bounds
    G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
    closeness = nx.closeness_centrality(G, distance="length")
    edge_closeness = {
        edge: (closeness[edge[0]] + closeness[edge[1]]) / 2 for edge in G.edges
    }
    init_edge = [tuple(max(edge_closeness, key=edge_closeness.get))]
    for key in RCPARAMS:
        mpl.rcParams[key] = RCPARAMS[key]
    fig, axs = plt.subplots(len(GROWTH_STRATEGIES), len(STAGES), figsize=FIGSIZE)
    fig.tight_layout()
    for idx_met, (met, met_name) in enumerate(GROWTH_STRATEGIES.items()):
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
        for idx_sta, stage in enumerate(STAGES):
            ax = axs[idx_met][idx_sta]
            # Find the stage closest to the number of kilometer chosen
            idx_stage = find_closest_value_idx(metrics_growth["xx"], stage * 10**3)
            H = G.edge_subgraph(order_growth[: idx_stage + 2] + init_edge)
            temp_gdf_nodes, temp_gdf_edges = mp.nx_to_gdf(H, points=True, lines=True)
            temp_gdf_nodes.plot(ax=ax, color="black", zorder=3)
            temp_gdf_edges.plot(ax=ax, color="black", zorder=2)
            ax.set_xlim([bb[0] * (1 - BB_PAD), bb[2] * (1 + BB_PAD)])
            ax.set_ylim([bb[1] * (1 - BB_PAD), bb[3] * (1 + BB_PAD)])
            ax.spines[:].set_visible(False)
            ax.set_xticks([])
            ax.set_yticks([])
    for idx_sta, stage in enumerate(STAGES):
        axs[0][idx_sta].xaxis.set_label_position("top")
        axs[0][idx_sta].set_xlabel(f"${stage} km$", labelpad=LABEL_PAD)
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

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
from O_plot_bikenet_single_map import COLOR_SCHEME_DICT
from O_plot_bikenet_single_map import FOLDERMAPS


GROWTH_STRATEGIES = {
    "coverage": "Coverage",
    "road_hierarchy_coverage": "Hierarchy,\ncoverage",
    "dual_betweenness": "Dual\nbetweenness",
    "road_hierarchy_directness": "Hierarchy,\ndirectness",
    "directness": "Directness",
}
FIGSIZE = [11.69, 8.27]
RCPARAMS = {
    "font.size": 60,
    "font.family": "sans-serif",
    "font.sans-serif": "Arial",
}
LABEL_PAD = 80
DPI = 300
CHOICE = 0
LW = 2
COLOR_NEW = "green"
STYLES_ARR = ["removed", "added", "separated"]


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
            & (G.edges[edge]["built_in"] == "2021-01-01")
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
    for color_scheme in ["colorful", "sober"]:
        for random_added in [True, False]:
            growth_strategies = GROWTH_STRATEGIES.copy()
            if random_added:
                growth_strategies["random"] = "Random"
            for style in STYLES_ARR:
                col = len(stages)
                row = len(growth_strategies) + 1
                if style == "separated":
                    col += 1
                fig, axs = plt.subplots(
                    row, col, figsize=[FIGSIZE[0] * col, FIGSIZE[1] * row]
                )
                for idx_met, (met, met_name) in enumerate(growth_strategies.items()):
                    idx_stage_bef = 0
                    axs[idx_met][0].set_ylabel(met_name, labelpad=LABEL_PAD)
                    foldermet = FOLDEROOT + f"Nothing/bs_{BUFF_SIZE}_{met}/"
                    if met == "coverage":
                        foldermet += f"{met}_{CHOICE:03}/"
                    elif met == "random":
                        foldermet += f"{met}_042/"
                    with open(foldermet + "order_growth.json") as f:
                        order_growth = json.load(f)
                    order_growth = [
                        tuple((tuple(val[0]), tuple(val[1]), val[2]))
                        for val in order_growth
                    ]
                    with open(foldermet + "metrics_growth.json") as f:
                        metrics_growth = json.load(f)
                    for idx_sta, stage in enumerate(stages):
                        ax = axs[idx_met][idx_sta]
                        # Find the stage closest to the number of kilometer chosen
                        idx_stage = find_closest_value_idx(
                            metrics_growth["xx"], stage * 10**3
                        )
                        if idx_sta == 0:
                            H = G.edge_subgraph(init_edge)
                            temp_gdf_edges = mp.nx_to_gdf(H, points=False, lines=True)
                            temp_gdf_edges.plot(
                                ax=ax,
                                color=COLOR_SCHEME_DICT[color_scheme][0],
                                zorder=2,
                                linewidth=LW,
                                capstyle="round",
                                joinstyle="round",
                            )
                            H = G.edge_subgraph(order_growth[: idx_stage + 2])
                            temp_gdf_edges = mp.nx_to_gdf(H, points=False, lines=True)
                            temp_gdf_edges.plot(
                                ax=ax,
                                color=COLOR_NEW,
                                zorder=3,
                                linewidth=LW + 3.5,
                                capstyle="round",
                                joinstyle="round",
                            )
                        else:
                            H = G.edge_subgraph(
                                order_growth[: idx_stage_bef + 2] + init_edge
                            )
                            temp_gdf_edges = mp.nx_to_gdf(H, points=False, lines=True)
                            temp_gdf_edges.plot(
                                ax=ax,
                                color=COLOR_SCHEME_DICT[color_scheme][0],
                                zorder=2,
                                linewidth=LW,
                                capstyle="round",
                                joinstyle="round",
                            )
                            H = G.edge_subgraph(
                                order_growth[idx_stage_bef + 1 : idx_stage + 2]
                            )
                            temp_gdf_edges = mp.nx_to_gdf(H, points=False, lines=True)
                            temp_gdf_edges.plot(
                                ax=ax,
                                color=COLOR_NEW,
                                zorder=3,
                                linewidth=LW + 3.5,
                                capstyle="round",
                                joinstyle="round",
                            )
                        idx_stage_bef = idx_stage
                        ax.set_xlim([bb[0], bb[2]])
                        ax.set_ylim([bb[1], bb[3]])
                        ax.spines[:].set_visible(False)
                        ax.set_xticks([])
                        ax.set_yticks([])
                        if (idx_sta == 2) & (style == "added"):
                            gdf_edges.plot(
                                ax=ax,
                                color=COLOR_SCHEME_DICT[color_scheme][1],
                                zorder=1,
                                linewidth=LW - 0.8,
                                capstyle="round",
                                joinstyle="round",
                            )
                    if style == "separated":
                        ax = axs[idx_met][-1]
                        ax.set_xlim([bb[0], bb[2]])
                        ax.set_ylim([bb[1], bb[3]])
                        ax.spines[:].set_visible(False)
                        ax.set_xticks([])
                        ax.set_yticks([])
                        H = G.edge_subgraph(
                            [
                                edge
                                for edge in G.edges
                                if edge not in order_growth[: idx_stage + 2] + init_edge
                            ]
                        )
                        temp_gdf_edges = mp.nx_to_gdf(H, points=False, lines=True)
                        temp_gdf_edges.plot(
                            ax=ax,
                            color=COLOR_SCHEME_DICT[color_scheme][1],
                            zorder=3,
                            linewidth=LW + 3.5,
                            capstyle="round",
                            joinstyle="round",
                        )
                axs[-1][0].set_ylabel(
                    "Empirical", labelpad=LABEL_PAD, multialignment="center"
                )
                gdf_edges[gdf_edges["built_in"] == "2021-01-01"].plot(
                    ax=axs[-1][0], color="white", capstyle="round", joinstyle="round"
                )
                gdf_edges[gdf_edges["built_in"] == "2021-01-01"].plot(
                    ax=axs[-1][1],
                    color=COLOR_NEW,
                    linewidth=LW + 3.5,
                    capstyle="round",
                    joinstyle="round",
                )
                gdf_edges[gdf_edges["built_in"] == "2021-01-01"].plot(
                    ax=axs[-1][2],
                    color=COLOR_SCHEME_DICT[color_scheme][0],
                    linewidth=LW,
                    capstyle="round",
                    joinstyle="round",
                )
                gdf_edges[~gdf_edges["built_in"].isin(["No", "2021-01-01"])].plot(
                    ax=axs[-1][2],
                    color=COLOR_NEW,
                    linewidth=LW + 3.5,
                    capstyle="round",
                    joinstyle="round",
                )
                if style == "added":
                    gdf_edges[gdf_edges["built_in"] == "No"].plot(
                        ax=axs[-1][2],
                        color=COLOR_SCHEME_DICT[color_scheme][1],
                        linewidth=LW - 0.8,
                        capstyle="round",
                        joinstyle="round",
                    )
                elif style == "separated":
                    axs[0][3].set_title("Missing")
                    ax = axs[-1][3]
                    ax.set_xlim([bb[0], bb[2]])
                    ax.set_ylim([bb[1], bb[3]])
                    ax.spines[:].set_visible(False)
                    ax.set_xticks([])
                    ax.set_yticks([])
                    gdf_edges[gdf_edges["built_in"] == "No"].plot(
                        ax=ax,
                        color=COLOR_SCHEME_DICT[color_scheme][1],
                        linewidth=LW + 3.5,
                        capstyle="round",
                        joinstyle="round",
                    )
                for i in range(len(stages)):
                    ax = axs[-1][i]
                    ax.set_xlim([bb[0], bb[2]])
                    ax.set_ylim([bb[1], bb[3]])
                    ax.spines[:].set_visible(False)
                    ax.set_xticks([])
                    ax.set_yticks([])
                for idx_sta, stage in enumerate(stages):
                    axs[0][idx_sta].set_title(f"${stage}$ km")
                    if stage == 124:
                        axs[-1][idx_sta].set_xlabel(
                            "2021", labelpad=LABEL_PAD, fontsize=RCPARAMS["font.size"]
                        )
                    elif stage == 200:
                        axs[-1][idx_sta].set_xlabel(
                            "2026", labelpad=LABEL_PAD, fontsize=RCPARAMS["font.size"]
                        )
                fig.tight_layout()
                filename = f"Growth_steps_pareto_{style}"
                if random_added:
                    filename += "_random"
                filename += f"_{color_scheme}.png"
                fig.savefig(
                    FOLDERMAPS + filename,
                    dpi=DPI,
                    bbox_inches="tight",
                    pad_inches=0.01,
                )


def find_closest_value_idx(list_values, target_value):
    lst = np.asarray(list_values)
    return (np.abs(lst - target_value)).argmin()


if __name__ == "__main__":
    main()

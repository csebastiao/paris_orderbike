# -*- coding: utf-8 -*-
"""
Replicate the real growth order on Paris graph.
"""

import os
import json
import networkx as nx
import geopandas as gpd
import momepy as mp
from G_grow_bikenet import BUFF_SIZE, FOLDEROOT, END_FOLDERS
from paris_orderbike.metrics import directness, coverage

TIMESTAMPS = [
    "2021-01-01",
    "2023-05-17",
    "2023-10-01",
    "2024-01-15",
    "2024-04-04",
    "2024-08-22",
    "2024-12-22",
    "2025-06-02",
    "2026-01-28",
    "No",
]


def main():
    for end_folder in END_FOLDERS:
        folder_save = FOLDEROOT + end_folder + "/"
        if not os.path.exists(folder_save):
            os.makedirs(folder_save)
        gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
        G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
        if folder_save.split("/")[-2] == "2021":
            init_edge = [
                edge for edge in G.edges if G.edges[edge]["built_in"] == "2021-01-01"
            ]
        elif folder_save.split("/")[-2] == "2026":
            init_edge = [
                edge for edge in G.edges if G.edges[edge]["built_in"] == "2026-01-28"
            ]
        elif folder_save.split("/")[-2] == "Nothing":
            closeness = nx.closeness_centrality(G, distance="length")
            edge_closeness = {
                edge: (closeness[edge[0]] + closeness[edge[1]]) / 2
                for edge in G.edges
                if (
                    (G.edges[edge]["highway"] == "primary")
                    & (G.edges[edge]["level"] == "primary")
                )
            }
            init_edge = [max(edge_closeness, key=edge_closeness.get)]
        G_init = G.edge_subgraph(init_edge)
        tot_length = [sum([G_init.edges[e]["length"] for e in G_init.edges])]
        dir_real = [directness(G_init)]
        cov_real = [coverage(G_init, BUFF_SIZE)]
        num_ccs = [nx.number_connected_components(G_init)]
        length_lcc = [sum([G_init.edges[e]["length"] for e in G_init.edges])]
        for i in range(len(TIMESTAMPS)):
            H = G.edge_subgraph(
                [e for e in G.edges if G.edges[e]["built_in"] in TIMESTAMPS[: i + 1]]
            )
            tot_length.append(sum([H.edges[e]["length"] for e in H.edges]))
            dir_real.append(directness(H))
            cov_real.append(coverage(H, BUFF_SIZE))
            cc = list(nx.connected_components(H))
            num_ccs.append(len(cc))
            length_lcc.append(
                max(
                    [
                        sum([H.edges[e]["length"] for e in H.subgraph(comp).edges])
                        for comp in cc
                    ]
                )
            )
        met_dict = {}
        met_dict["xx"] = tot_length
        met_dict["coverage"] = cov_real
        met_dict["directness"] = dir_real
        met_dict["num_cc"] = num_ccs
        met_dict["length_lcc"] = length_lcc
        foldertime = folder_save + f"/bs_{BUFF_SIZE}_real/"
        if not os.path.exists(foldertime):
            os.makedirs(foldertime)
        with open(foldertime + "metrics_growth.json", "w") as f:
            json.dump(met_dict, f)


if __name__ == "__main__":
    main()

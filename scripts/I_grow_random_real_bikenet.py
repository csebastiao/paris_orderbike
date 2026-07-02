# -*- coding: utf-8 -*-
"""
Replicate the real growth order on Paris graph, but assuming a disconnected random growth between timestamps.
"""

import os
import json
import geopandas as gpd
import momepy as mp
import networkx as nx
import numpy as np
import shapely
from G_grow_bikenet import BUFF_SIZE, FOLDEROOT, END_FOLDERS, init_gdf
from paris_orderbike.metrics import directness

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
NUM_RAND_REAL_TRIAL = 1000
RECOMPUTE = False
MET_DICT_KEYS = ["xx", "directness", "coverage", "num_cc", "length_lcc"]
SEED = None


def main():
    rng = np.random.default_rng(seed=SEED)
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    # Find initial edge if from scratch and remove it from the list of edges to shuffle
    gdf_nothing_edges = init_gdf(gdf_edges, "Nothing")
    G = mp.gdf_to_nx(gdf_nothing_edges, integer_labels=False, preserve_index=True)
    edges_t = {
        t: np.array(
            [
                tuple(edge)
                for edge in G.edges
                if ((G.edges[edge]["built_in"] == t) & (G.edges[edge]["built"] == 0))
            ],
            dtype=object,
        )
        for t in TIMESTAMPS
    }
    for end_folder, pos in zip(END_FOLDERS, [0, 1, -1]):
        gdf_time_edges = init_gdf(gdf_edges, end_folder)
        G_time = mp.gdf_to_nx(gdf_time_edges, integer_labels=False, preserve_index=True)
        folder_save = FOLDEROOT + end_folder + "/"
        if not os.path.exists(folder_save):
            os.makedirs(folder_save)
        for i in range(NUM_RAND_REAL_TRIAL):
            foldername = folder_save + f"bs_{BUFF_SIZE}_real_random/real_random_{i:03}/"
            if os.path.exists(foldername) and not RECOMPUTE:
                pass
            else:
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                order_growth = [
                    tuple(val)
                    for arr in [rng.permutation(edges_t[t]) for t in TIMESTAMPS[pos:]]
                    for val in arr
                ]
                met_dict = compute_metrics(G_time, order_growth, BUFF_SIZE)
                with open(foldername + "order_growth.json", "w") as f:
                    json.dump(order_growth, f)
                with open(foldername + "metrics_growth.json", "w") as f:
                    json.dump(met_dict, f)


def compute_metrics(G, order_growth, buff_size):
    init_edges = [edge for edge in G.edges if G.edges[edge]["built"] == 1]
    G_init = G.edge_subgraph(init_edges)
    actual_buff_geom = (
        mp.nx_to_gdf(G_init, points=False, lines=True).buffer(buff_size).union_all()
    )
    met_dict = {}
    met_dict["xx"] = [sum([G_init.edges[e]["length"] for e in G_init.edges])]
    met_dict["directness"] = [directness(G_init)]
    met_dict["coverage"] = [actual_buff_geom.area]
    cc = list(nx.connected_components(G_init))
    met_dict["num_cc"] = [len(cc)]
    met_dict["length_lcc"] = [
        max(
            [
                sum([G_init.edges[e]["length"] for e in G_init.subgraph(comp).edges])
                for comp in cc
            ]
        )
    ]
    current_edges = init_edges.copy()
    for edge in order_growth:
        current_edges += [edge]
        H = G.edge_subgraph(current_edges)
        met_dict["xx"].append(sum([H.edges[e]["length"] for e in H.edges]))
        # met_dict["xx"].append(met_dict["xx"][-1] + G.edges[edge]["length"])
        met_dict["directness"].append(directness(H))
        actual_buff_geom = shapely.unary_union(
            [
                actual_buff_geom,
                G.edges[edge]["geometry"].buffer(buff_size),
            ]
        )
        met_dict["coverage"].append(actual_buff_geom.area)
        cc = list(nx.connected_components(H))
        met_dict["num_cc"].append(len(cc))
        met_dict["length_lcc"].append(
            max(
                [
                    sum([H.edges[e]["length"] for e in H.subgraph(comp).edges])
                    for comp in cc
                ]
            )
        )
    return met_dict


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Grow Paris bicycle network.
"""

import geopandas as gpd
import momepy as mp
import networkx as nx
from paris_orderbike.growth import Orderbike
import json
import os

FOLDEROOT = "./data/processed/"
PRESET = [
    "directness",
    "coverage",
    "hierarchy",
    "random",
    "betweenness",
    "closeness",
    "dual_betweenness",
    "dual_closeness",
    "hierarchy_coverage",
    "hierarchy_directness",
]
ROAD_HIERARCHY_MAP = {
    "primary": 4,
    "secondary": 3,
    "tertiary": 2,
    "quaternary": 1,
}
BIKE_HIERARCHY_MAP = {
    "primary": 2,
    "secondary": 1,
}
END_FOLDERS = [
    "Nothing",
    "2021",
    "2026",
]
BUFF_SIZE = 400
NUM_RAND_TRIAL = 1000
NUM_HIER_TRIAL = 1000
NUM_COV_TRIAL = 20
RECOMPUTE = False


def main():
    gdf_raw = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    for end_folder in END_FOLDERS:
        folder_save = FOLDEROOT + end_folder + "/"
        if not os.path.exists(folder_save):
            os.makedirs(folder_save)
        gdf_edges = init_gdf(gdf_raw, end_folder)
        for met in PRESET:
            if met == "random":
                G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
                for i in range(NUM_RAND_TRIAL):
                    foldername = folder_save + f"bs_{BUFF_SIZE}_{met}/{met}_{i:03}/"
                    run_and_save_orderbike(G, met, BUFF_SIZE, foldername, RECOMPUTE)
            elif met == "hierarchy":
                for args in [
                    ["highway", ROAD_HIERARCHY_MAP, "road"],
                    # ["level", BIKE_HIERARCHY_MAP, "bikenet"],
                ]:
                    gdf_edges["hierarchy"] = gdf_edges[args[0]].map(args[1])
                    G = mp.gdf_to_nx(
                        gdf_edges, integer_labels=False, preserve_index=True
                    )
                    for i in range(NUM_HIER_TRIAL):
                        foldername = (
                            folder_save
                            + f"bs_{BUFF_SIZE}_{args[2]}_{met}/{args[2]}_{met}_{i:03}/"
                        )
                        run_and_save_orderbike(G, met, BUFF_SIZE, foldername, RECOMPUTE)
            elif met in ["hierarchy_coverage", "hierarchy_directness"]:
                for args in [
                    ["highway", ROAD_HIERARCHY_MAP, "road"],
                    # ["level", BIKE_HIERARCHY_MAP, "bikenet"],
                ]:
                    gdf_edges["hierarchy"] = gdf_edges[args[0]].map(args[1])
                    G = mp.gdf_to_nx(
                        gdf_edges, integer_labels=False, preserve_index=True
                    )
                    foldername = folder_save + f"bs_{BUFF_SIZE}_{args[2]}_{met}/"
                    run_and_save_orderbike(G, met, BUFF_SIZE, foldername, RECOMPUTE)
            elif met == "coverage":
                G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
                for i in range(NUM_COV_TRIAL):
                    foldername = folder_save + f"bs_{BUFF_SIZE}_{met}/{met}_{i:03}/"
                    run_and_save_orderbike(G, met, BUFF_SIZE, foldername, RECOMPUTE)
            else:
                G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
                foldername = folder_save + f"bs_{BUFF_SIZE}_{met}/"
                run_and_save_orderbike(G, met, BUFF_SIZE, foldername, RECOMPUTE)


def init_gdf(gdf_edges, end_folder):
    gdf = gdf_edges.copy()
    if end_folder == "2021":
        gdf["built"] = gdf["built_in"].apply(lambda x: 1 if x == "2021-01-01" else 0)
    elif end_folder == "2026":
        gdf["built"] = gdf["built_in"].apply(lambda x: 1 if x != "No" else 0)
    elif end_folder == "Nothing":
        G = mp.gdf_to_nx(gdf, integer_labels=False, preserve_index=True)
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
        choice = max(edge_closeness, key=edge_closeness.get)
        gdf["built"] = gdf.apply(
            lambda df: (
                1
                if (
                    ((df["from"] == str(choice[0])) & (df["to"] == str(choice[1])))
                    or ((df["to"] == str(choice[0])) & (df["from"] == str(choice[1])))
                )
                else 0
            ),
            axis=1,
        )
    return gdf


def run_and_save_orderbike(G, met, BUFF_SIZE, foldername, recompute):
    if os.path.exists(foldername) and not recompute:
        pass
    else:
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        odb = Orderbike(
            G,
            preset=met,
            buff_size=BUFF_SIZE,
            built=True,
            keep_connected=True,
        )
        odb.grow()
        order_growth = odb.get_growth_order()
        met_dict = odb.get_metrics_dict()
        with open(foldername + "order_growth.json", "w") as f:
            json.dump(order_growth, f)
        with open(foldername + "metrics_growth.json", "w") as f:
            json.dump(met_dict, f)


if __name__ == "__main__":
    main()

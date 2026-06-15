# -*- coding: utf-8 -*-
"""
Grow Paris bicycle network.
"""

import geopandas as gpd
import momepy as mp
from paris_orderbike.growth import Orderbike
import json
import os

FOLDER_IN = "./data/processed/"
FOLDER_OUT = "./data/processed/2021/"
PRESET = [
    "directness",
    "coverage",
    "hierarchy",
    "hierarchy_coverage",
    "betweenness",
    "closeness",
    "random",
    # "dual_betweenness",
    # "dual_closeness",
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
BUFF_SIZE = 400
NUM_RAND_TRIAL = 500
NUM_HIER_TRIAL = 20
NUM_COV_TRIAL = 20
BUILT = True


def main():
    if not os.path.exists(FOLDER_OUT):
        os.makedirs(FOLDER_OUT)
    gdf_edges = gpd.read_file(FOLDER_OUT + "bikenet_edges.gpkg")
    if BUILT:
        gdf_edges["built"] = gdf_edges["built_in"].apply(
            lambda x: 1 if x == "2021-01-01" else 0
        )
    for met in PRESET:
        if met == "random":
            G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
            for i in range(NUM_RAND_TRIAL):
                foldername = FOLDER_OUT + f"bs_{BUFF_SIZE}_{met}/{met}_{i:03}/"
                run_and_save_orderbike(G, met, BUFF_SIZE, BUILT, foldername)
        elif met == "hierarchy":
            for args in [
                ["highway", ROAD_HIERARCHY_MAP, "road"],
                ["level", BIKE_HIERARCHY_MAP, "bikenet"],
            ]:
                gdf_edges["hierarchy"] = gdf_edges[args[0]].map(args[1])
                G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
                for i in range(NUM_HIER_TRIAL):
                    foldername = (
                        FOLDER_OUT
                        + f"bs_{BUFF_SIZE}_{args[2]}_{met}/{args[2]}_{met}_{i:03}/"
                    )
                    run_and_save_orderbike(G, met, BUFF_SIZE, BUILT, foldername)
        elif met == "hierarchy_coverage":
            for args in [
                ["highway", ROAD_HIERARCHY_MAP, "road"],
                ["level", BIKE_HIERARCHY_MAP, "bikenet"],
            ]:
                gdf_edges["hierarchy"] = gdf_edges[args[0]].map(args[1])
                G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
                foldername = FOLDER_OUT + f"bs_{BUFF_SIZE}_{args[2]}_{met}/"
                run_and_save_orderbike(G, met, BUFF_SIZE, BUILT, foldername)
        elif met == "coverage":
            G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
            for i in range(NUM_COV_TRIAL):
                foldername = FOLDER_OUT + f"bs_{BUFF_SIZE}_{met}/{met}_{i:03}/"
                run_and_save_orderbike(G, met, BUFF_SIZE, BUILT, foldername)
        else:
            G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
            foldername = FOLDER_OUT + f"bs_{BUFF_SIZE}_{met}/"
            run_and_save_orderbike(G, met, BUFF_SIZE, BUILT, foldername)


def run_and_save_orderbike(G, met, BUFF_SIZE, BUILT, foldername):
    odb = Orderbike(
        G,
        preset=met,
        buff_size=BUFF_SIZE,
        built=BUILT,
        keep_connected=True,
    )
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    odb.grow()
    order_growth = odb.get_growth_order()
    met_dict = odb.get_metrics_dict()
    with open(foldername + "order_growth.json", "w") as f:
        json.dump(order_growth, f)
    with open(foldername + "metrics_growth.json", "w") as f:
        json.dump(met_dict, f)


if __name__ == "__main__":
    main()

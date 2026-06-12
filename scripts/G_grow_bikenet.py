# -*- coding: utf-8 -*-
"""
Grow Paris bicycle network.
"""

import geopandas as gpd
import momepy as mp
from paris_orderbike.growth import Orderbike
import json
import os

FOLDEROOT = "./data/processed/"
PRESET = [
    # "directness",
    # "coverage",
    # "hierarchy",
    "hierarchy_coverage",
    # "betweenness",
    # "dual_betweenness",
    # "closeness",
    # "dual_closeness",
    # "random",
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


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    for met in PRESET:
        if met == "random":
            G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
            for i in range(NUM_RAND_TRIAL):
                odb = Orderbike(
                    G, preset=met, buff_size=BUFF_SIZE, built=False, keep_connected=True
                )
                foldername = FOLDEROOT + f"bs_{BUFF_SIZE}_{met}/{met}_{i:03}/"
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                odb.grow()
                order_growth = odb.get_growth_order()
                met_dict = odb.get_metrics_dict()
                with open(foldername + "order_growth.json", "w") as f:
                    json.dump(order_growth, f)
                with open(foldername + "metrics_growth.json", "w") as f:
                    json.dump(met_dict, f)
        elif met == "hierarchy":
            for args in [
                # ["highway", ROAD_HIERARCHY_MAP, "road"],
                ["level", BIKE_HIERARCHY_MAP, "bikenet"],
            ]:
                gdf_edges["hierarchy"] = gdf_edges[args[0]].map(args[1])
                G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
                for i in range(NUM_HIER_TRIAL):
                    odb = Orderbike(
                        G,
                        preset=met,
                        buff_size=BUFF_SIZE,
                        built=False,
                        keep_connected=True,
                    )
                    foldername = (
                        FOLDEROOT
                        + f"bs_{BUFF_SIZE}_{args[2]}_{met}/{args[2]}_{met}_{i:03}/"
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
        elif met == "hierarchy_coverage":
            for args in [
                ["highway", ROAD_HIERARCHY_MAP, "road"],
                ["level", BIKE_HIERARCHY_MAP, "bikenet"],
            ]:
                gdf_edges["hierarchy"] = gdf_edges[args[0]].map(args[1])
                G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
                odb = Orderbike(
                    G, preset=met, buff_size=BUFF_SIZE, built=False, keep_connected=True
                )
                foldername = FOLDEROOT + f"bs_{BUFF_SIZE}_{args[2]}_{met}/"
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                odb.grow()
                order_growth = odb.get_growth_order()
                met_dict = odb.get_metrics_dict()
                with open(foldername + "order_growth.json", "w") as f:
                    json.dump(order_growth, f)
                with open(foldername + "metrics_growth.json", "w") as f:
                    json.dump(met_dict, f)
        else:
            G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
            for met in PRESET:
                for i in range(NUM_RAND_TRIAL):
                    odb = Orderbike(
                        G,
                        preset=met,
                        buff_size=BUFF_SIZE,
                        built=False,
                        keep_connected=True,
                    )
                    foldername = FOLDEROOT + f"bs_{BUFF_SIZE}_{met}/{met}_{i:03}/"
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

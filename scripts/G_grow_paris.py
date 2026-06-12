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
    "coverage",
    # "hierarchical",
    # "betweenness",
    # "closeness",
    # "random",
]
BUFF_SIZE = 400
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
# FIXME coverage


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    gdf_edges["hierarchy"] = gdf_edges["level"].map(BIKE_HIERARCHY_MAP)
    G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
    for met in PRESET:
        odb = Orderbike(
            G, preset=met, buff_size=BUFF_SIZE, built=False, keep_connected=True
        )
        foldername = FOLDEROOT + f"bs_{BUFF_SIZE}_{met}/"
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

import json
import os

import geopandas as gpd
import momepy as mp
import networkx as nx

from paris_orderbike.growth import Orderbike

FOLDEROOT = "./data/processed/"
END_FOLDERS = [
    "Nothing",
    "2021",
    "2026",
]
NUM_RAND_TRIAL = 1000
BUFFER_SIZE = 400


def main():
    gdf_raw = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    for end_folder in END_FOLDERS:
        folder_save = FOLDEROOT + end_folder + "/"
        if not os.path.exists(folder_save):
            os.makedirs(folder_save)
        gdf_edges = init_gdf(gdf_raw, end_folder)
        G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
        for i in range(NUM_RAND_TRIAL):
            foldername = (
                folder_save + f"bs_{BUFFER_SIZE}_random_relaxed/random_relaxed_{i:03}/"
            )
            run_and_save_orderbike(
                G,
                "random_relaxed",
                BUFFER_SIZE,
                foldername,
                False,
            )


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


def run_and_save_orderbike(G, met, buffer_size, foldername, recompute):
    if os.path.exists(foldername) and not recompute:
        pass
    else:
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        odb = Orderbike(
            G,
            preset=met,
            buff_size=buffer_size,
            built=True,
            keep_connected=False,
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

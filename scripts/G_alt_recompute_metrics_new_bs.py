"""
Recompute the metrics for a new buffer size for orders that are not impacted by the buffer size.
"""

import json
import os

import geopandas as gpd
import momepy as mp
import networkx as nx
import shapely

from paris_orderbike.metrics import directness

FOLDEROOT = "./data/processed/"
END_FOLDERS = ["Nothing", "2021", "2026"]
PRESET = [
    "directness",
    "road_hierarchy",
    "random",
    "betweenness",
    "closeness",
    "dual_betweenness",
    "dual_closeness",
    "road_hierarchy_directness",
    "real_random",
]
NUM_RAND = 1000
OLD_BUFFER = 400
NEW_BUFFER = 500


def main():
    gdf_raw = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    for end in END_FOLDERS:
        gdf_end = init_gdf(gdf_raw, end)
        G = mp.gdf_to_nx(gdf_end, integer_labels=False, preserve_index=True)
        for met in PRESET:
            foldermet = FOLDEROOT + end + f"/bs_{OLD_BUFFER}_" + met + "/"
            if met in ["random", "road_hierarchy", "real_random"]:
                for i in range(NUM_RAND):
                    folderord = foldermet + met + f"_{i:03}/"
                    recompute_metrics(folderord, G)
            else:
                recompute_metrics(foldermet, G)


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


def recompute_metrics(folder, G):
    with open(folder + "order_growth.json") as f:
        order_growth = json.load(f)
    order_growth = [(tuple(val[0]), tuple(val[1]), val[2]) for val in order_growth]
    folder_out = folder.replace(f"bs_{OLD_BUFFER}", f"bs_{NEW_BUFFER}")
    if not os.path.exists(folder_out):
        os.makedirs(folder_out)
    with open(folder_out + "order_growth.json", "w") as f:
        json.dump(order_growth, f)
    met_dict = {}
    edgelist = [edge for edge in G.edges if G.edges[edge]["built"] == 1]
    H = G.edge_subgraph(edgelist)
    edge_buffered = shapely.unary_union(
        [H.edges[e]["geometry"].buffer(NEW_BUFFER) for e in H.edges]
    )
    met_dict["xx"] = [sum([H.edges[e]["length"] for e in H.edges])]
    met_dict["directness"] = [directness(H)]
    met_dict["coverage"] = [edge_buffered.area]
    cc = list(nx.connected_components(H))
    met_dict["num_cc"] = [len(cc)]
    met_dict["length_lcc"] = [
        max(
            [sum([H.edges[e]["length"] for e in H.subgraph(comp).edges]) for comp in cc]
        )
    ]
    for edge in order_growth:
        edgelist.append(edge)
        H = G.edge_subgraph(edgelist)
        met_dict["xx"].append(sum([H.edges[e]["length"] for e in H.edges]))
        met_dict["directness"].append(directness(H))
        edge_buffered = shapely.unary_union(
            [edge_buffered, H.edges[edge]["geometry"].buffer(NEW_BUFFER)]
        )
        met_dict["coverage"].append(edge_buffered.area)
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
    with open(folder_out + "metrics_growth.json", "w") as f:
        json.dump(met_dict, f)


if __name__ == "__main__":
    main()

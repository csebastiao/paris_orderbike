"""
Add population covered for all orders.
"""

import json

import geopandas as gpd
import momepy as mp
import networkx as nx
from Ga_grow_bikenet import NUM_COV_TRIAL, NUM_HIER_TRIAL, NUM_RAND_TRIAL, init_gdf
from I_grow_random_real_bikenet import NUM_RAND_REAL_TRIAL

FOLDEROOT = "./data/processed/"
BUFF_SIZE = 400
MET = [
    "directness",
    "coverage",
    "betweenness",
    "closeness",
    "dual_betweenness",
    "dual_closeness",
    "road_hierarchy_coverage",
    "road_hierarchy_directness",
    "real",
    "real_random",
    "road_hierarchy",
    "random",
    "random_disconnected",
    "random_relaxed",
]
TRIAL_DICT = {
    "coverage": NUM_COV_TRIAL,
    "road_hierarchy": NUM_HIER_TRIAL,
    "random": NUM_RAND_TRIAL,
    "random_relaxed": NUM_RAND_TRIAL,
    "random_disconnected": NUM_RAND_TRIAL,
    "real_random": NUM_RAND_REAL_TRIAL,
}
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
START_TIMESTAMPS = {
    "Nothing": 0,
    "2021": 1,
    "2026": 9,
}
RECOMPUTE = False


def main():
    for end_folder in ["2021", "2026", "Nothing"]:
        gdf_bikenet = gpd.read_file(FOLDEROOT + "bikenet_wpop_edges.gpkg")
        gdf_edges = init_gdf(gdf_bikenet, end_folder)
        G_full = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
        for met in MET:
            if met in [
                "coverage",
                "road_hierarchy",
                "random",
                "real_random",
                "random_disconnected",
                "random_relaxed",
            ]:
                num_trials = TRIAL_DICT[met]
                for i in range(num_trials):
                    with open(
                        FOLDEROOT
                        + end_folder
                        + f"/bs_{BUFF_SIZE}_{met}/{met}_{i:03}/order_growth.json"
                    ) as f:
                        order_growth = json.load(f)
                    with open(
                        FOLDEROOT
                        + end_folder
                        + f"/bs_{BUFF_SIZE}_{met}/{met}_{i:03}/metrics_growth.json"
                    ) as f:
                        met_dict = json.load(f)
                    if "pop_buff" not in met_dict or RECOMPUTE:
                        met_dict["pop_buff"] = compute_pop_buff_order(
                            gdf_bikenet, G_full, order_growth
                        )
                        with open(
                            FOLDEROOT
                            + end_folder
                            + f"/bs_{BUFF_SIZE}_{met}/{met}_{i:03}/metrics_growth.json",
                            "w",
                        ) as f:
                            json.dump(met_dict, f)
            elif met == "real":
                with open(
                    FOLDEROOT
                    + end_folder
                    + f"/bs_{BUFF_SIZE}_{met}/metrics_growth.json"
                ) as f:
                    met_dict = json.load(f)
                if "pop_buff" not in met_dict or RECOMPUTE:
                    start_end = START_TIMESTAMPS[end_folder]
                    G_built = G_full.edge_subgraph(
                        [
                            edge
                            for edge in G_full.edges
                            if G_full.edges[edge]["built_in"] in TIMESTAMPS[:start_end]
                        ]
                    )
                    real_pops = [
                        compute_pop_graph(
                            buffer_graph(G_built, G_full, buffer=BUFF_SIZE)
                        )
                    ]
                    for i in range(len(TIMESTAMPS[start_end:])):
                        G_built = G_full.edge_subgraph(
                            [
                                edge
                                for edge in G_full.edges
                                if G_full.edges[edge]["built_in"]
                                in TIMESTAMPS[: start_end + i + 1]
                            ]
                        )
                        real_pops.append(
                            compute_pop_graph(
                                buffer_graph(G_built, G_full, buffer=BUFF_SIZE)
                            )
                        )
                    met_dict["pop_buff"] = real_pops
                    with open(
                        FOLDEROOT
                        + end_folder
                        + f"/bs_{BUFF_SIZE}_{met}/metrics_growth.json",
                        "w",
                    ) as f:
                        json.dump(met_dict, f)
            else:
                with open(
                    FOLDEROOT + end_folder + f"/bs_{BUFF_SIZE}_{met}/order_growth.json"
                ) as f:
                    order_growth = json.load(f)
                with open(
                    FOLDEROOT
                    + end_folder
                    + f"/bs_{BUFF_SIZE}_{met}/metrics_growth.json"
                ) as f:
                    met_dict = json.load(f)
                if "pop_buff" not in met_dict or RECOMPUTE:
                    met_dict["pop_buff"] = compute_pop_buff_order(
                        gdf_bikenet, G_full, order_growth
                    )
                    with open(
                        FOLDEROOT
                        + end_folder
                        + f"/bs_{BUFF_SIZE}_{met}/metrics_growth.json",
                        "w",
                    ) as f:
                        json.dump(met_dict, f)


def compute_pop_buff_order(gdf_edges, G_full, order_growth):
    gdf_end = gdf_edges.copy()
    # Make order growth readable
    order_growth = [(tuple(val[0]), tuple(val[1]), val[2]) for val in order_growth]
    # Swap u and v to find all edges
    order_growth_rev = [(tuple(val[1]), tuple(val[0]), val[2]) for val in order_growth]
    order_dict = {val: idx for idx, val in enumerate(order_growth)}
    order_dict_rev = {val: idx for idx, val in enumerate(order_growth_rev)}
    # Transfrom strings into tuple of float
    gdf_end["from"] = gdf_end["from"].apply(
        lambda x: (float(x.split(",")[0][1:]), float(x.split(",")[1][1:-1]))
    )
    gdf_end["to"] = gdf_end["to"].apply(
        lambda x: (float(x.split(",")[0][1:]), float(x.split(",")[1][1:-1]))
    )
    gdf_end["key"] = gdf_end.apply(lambda df: (df["from"], df["to"], 0), axis=1)
    # Find order of growth for list of edges
    gdf_end["order"] = gdf_end["key"].map(order_dict)
    gdf_end["order_rev"] = gdf_end["key"].map(order_dict_rev)
    gdf_end["order_comb"] = gdf_end["order"].fillna(gdf_end["order_rev"])
    gdf_end["order_comb"] = gdf_end["order_comb"].fillna(-1).map(int)
    gdf_end = gdf_end.sort_values(by="order_comb")
    # Remove useless columns
    gdf_end = gdf_end[["level", "order_comb", "length", "pop", "geometry", "key"]]
    edges_current = [edge for edge in G_full.edges if G_full.edges[edge]["built"] == 1]
    G_current = G_full.edge_subgraph(edges_current)
    pop_buff_order = [
        compute_pop_graph(buffer_graph(G_current, G_full, buffer=BUFF_SIZE))
    ]
    for row in gdf_end[gdf_end["order_comb"] > -1].itertuples(index=False):
        edges_current.append(row.key)
        G_current = G_full.edge_subgraph(edges_current)
        pop_buff_order.append(
            compute_pop_graph(buffer_graph(G_current, G_full, buffer=BUFF_SIZE))
        )
    return pop_buff_order


def compute_pop_graph(G):
    return sum([G.edges[edge]["pop"] for edge in G.edges])


def buffer_graph(G_current, G_full, buffer=500):
    """
    Buffer a subgraph G_current of the graph G_full by adding to it any node and edges within a network distance of the buffer.
    """
    contact_nodes = find_contact_nodes(G_current, G_full)
    return G_full.edge_subgraph(
        {
            edge
            for edge_arr in [
                nx.ego_graph(G_full, n, radius=buffer, distance="length").edges
                for n in contact_nodes
            ]
            + [G_current.edges]
            for edge in edge_arr
        }
    )


def find_contact_nodes(G_current, G_full):
    """
    Find nodes that have both edges built and not built.
    """
    return [
        node
        for node in G_current.nodes
        if len(G_full.edges(node)) > len(G_current.edges(node))
    ]


if __name__ == "__main__":
    main()
